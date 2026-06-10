import json
import logging
import re

from agents.base import get_chat_client
from agents.prompts import SAFETY_AGENT_INSTRUCTIONS

logger = logging.getLogger(__name__)

UNSAFE_PATTERNS = [
    "you have ",
    "you definitely have",
    "stop taking",
    "do not see a doctor",
    "prescribe",
    "take this medication",
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


async def validate_response(response: str) -> dict:
    logger.info("SafetyAgent: validating response (%d chars)", len(response))
    client = get_chat_client()
    agent = client.as_agent(
        name="SafetyAgent",
        instructions=SAFETY_AGENT_INSTRUCTIONS,
    )

    lower = response.lower()
    flags = [p for p in UNSAFE_PATTERNS if p in lower]
    emergency = _detect_emergency(response)

    prompt = f"""
    Review this response for safety violations:
    {response}

    Known flags: {flags}
    Emergency symptoms detected: {emergency}
    Return JSON: {{"safe": true/false, "issues": [], "revised_response": "..."}}
    If emergency symptoms are present, advise seeking emergency care immediately.
    Always include a consult-your-doctor disclaimer if missing.
    """
    try:
        result = await agent.run(prompt)
        parsed = _parse_json_response(result.text)
    except Exception:
        logger.warning("SafetyAgent: LLM review failed, using rule-based fallback")
        parsed = {
            "safe": len(flags) == 0 and not emergency,
            "issues": flags + emergency,
            "revised_response": (
                "Your report suggests findings that should be discussed with a healthcare professional. "
                "Please consult your doctor. This is educational information, not medical advice."
            ),
        }

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

    logger.info(
        "SafetyAgent: safe=%s issues=%d",
        parsed.get("safe"),
        len(parsed.get("issues", [])),
    )
    return parsed
