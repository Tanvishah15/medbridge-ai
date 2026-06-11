import json
import logging
import re

from agents.base import get_chat_client, run_agent
from agents.logging_config import log_agent_input, log_agent_output
from agents.prompts import SAFETY_AGENT_INSTRUCTIONS

logger = logging.getLogger(__name__)

UNSAFE_STRING_PATTERNS = [
    "you definitely have",
    "stop taking",
    "stop your",
    "do not see a doctor",
    "prescribe",
    "take this medication",
    "times daily",
    " mg",
]

# "you have diabetes" — but NOT "you have been given" / "you have had"
UNSAFE_DIAGNOSIS_RE = re.compile(
    r"\byou have (?!been\b|had\b|any\b|a fever\b|not\b|no\b|an appointment\b|questions\b|to follow\b)\S",
    re.I,
)

REPORT_FRAMING_MARKERS = (
    "your report",
    "the report",
    "report shows",
    "report describes",
    "report indicates",
    "report recommends",
    "report says",
)

PRESCRIPTION_DRUGS = [
    "ibuprofen",
    "aspirin",
    "metformin",
    "acetaminophen",
    "paracetamol",
    "amoxicillin",
]

EMERGENCY_SYMPTOMS = [
    "chest pain",
    "difficulty breathing",
    "severe bleeding",
    "confusion",
]


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def _detect_emergency(text: str) -> list[str]:
    lower = text.lower()
    return [symptom for symptom in EMERGENCY_SYMPTOMS if symptom in lower]


def _is_report_based_explanation(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in REPORT_FRAMING_MARKERS)


def _detect_unsafe_flags(text: str) -> list[str]:
    lower = text.lower()
    flags = [pattern for pattern in UNSAFE_STRING_PATTERNS if pattern in lower]
    if UNSAFE_DIAGNOSIS_RE.search(text):
        flags.append("direct diagnosis phrasing")
    return flags


def _rule_based_review(response: str, flags: list[str], emergency: list[str]) -> dict:
    is_safe = len(flags) == 0 and not emergency
    if is_safe:
        return {
            "safe": True,
            "issues": [],
            "revised_response": response,
        }
    return {
        "safe": False,
        "issues": flags + emergency,
        "revised_response": (
            "Your report suggests findings that should be discussed with a healthcare professional. "
            "Please consult your doctor. This is educational information, not medical advice."
        ),
    }


def _detect_prescription_content(text: str) -> list[str]:
    lower = text.lower()
    issues = []
    if any(drug in lower for drug in PRESCRIPTION_DRUGS):
        issues.append("specific medication named")
    if re.search(r"\d+\s*mg", lower):
        issues.append("dosage specified")
    return issues


async def validate_response(response: str) -> dict:
    agent_name = "SafetyAgent"
    log_agent_input(agent_name, response=response)
    client = get_chat_client()

    flags = _detect_unsafe_flags(response)
    emergency = _detect_emergency(response)
    prescription_flags = _detect_prescription_content(response)
    all_flags = flags + prescription_flags

    if _is_report_based_explanation(response) and not emergency and not prescription_flags:
        if not flags or flags == ["direct diagnosis phrasing"]:
            parsed = {
                "safe": True,
                "issues": [],
                "revised_response": response,
            }
            log_agent_output(
                agent_name,
                safe=parsed.get("safe"),
                issues=parsed.get("issues"),
                revised_response=parsed.get("revised_response"),
            )
            return parsed

    if not all_flags and not emergency:
        parsed = _rule_based_review(response, all_flags, emergency)
        log_agent_output(
            agent_name,
            safe=parsed.get("safe"),
            issues=parsed.get("issues"),
            revised_response=parsed.get("revised_response"),
        )
        return parsed

    agent = client.as_agent(
        name="SafetyAgent",
        instructions=SAFETY_AGENT_INSTRUCTIONS,
    )
    prompt = f"""
    Review this response for safety violations:
    {response}

    Known flags: {all_flags}
    Emergency symptoms detected: {emergency}
    Report-based explanation: {_is_report_based_explanation(response)}
    Return JSON: {{"safe": true/false, "issues": [], "revised_response": "..."}}
    If emergency symptoms are present, advise seeking emergency care immediately.
    Always include a consult-your-doctor disclaimer if missing.
    """
    try:
        result = await run_agent(agent, prompt)
        parsed = _parse_json_response(result.text)
    except Exception:
        logger.warning("%s | LLM review failed, using rule-based fallback", agent_name)
        parsed = _rule_based_review(response, all_flags, emergency)

    if emergency:
        issues = list(parsed.get("issues", []))
        for symptom in emergency:
            if symptom not in issues:
                issues.append(symptom)
        parsed["issues"] = issues
        if "emergency" not in parsed.get("revised_response", "").lower():
            parsed["revised_response"] = (
                parsed.get("revised_response", response)
                + "\n\nSeek emergency care immediately for serious symptoms."
            )

    log_agent_output(
        agent_name,
        safe=parsed.get("safe"),
        issues=parsed.get("issues"),
        revised_response=parsed.get("revised_response"),
    )
    return parsed
