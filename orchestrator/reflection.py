import json
import logging
import re

from pydantic import BaseModel, Field

from agents.base import get_chat_client, run_agent
from agents.models import PatientContext, ReportStructure

logger = logging.getLogger(__name__)

REFLECTION_INSTRUCTIONS = """
You are the MedBridge Self-Reflection Critic.
After an explanation is generated, verify it is grounded in the provided knowledge.

Return JSON only:
{
  "grounded": true/false,
  "confidence": "high" | "medium" | "low",
  "missing_topics": ["topic1"],
  "follow_up_query": "optional knowledge re-query or empty string"
}

Mark confidence "low" if:
- Explanation invents facts not in knowledge
- Patient symptoms are not connected to report findings
- Important report findings are ignored

If confidence is low, provide a follow_up_query to retrieve missing grounded facts.
"""

CONFIDENCE_ORDER = {"high": 3, "medium": 2, "low": 1}


class ReflectionResult(BaseModel):
    grounded: bool = True
    confidence: str = "high"
    missing_topics: list[str] = Field(default_factory=list)
    follow_up_query: str = ""


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def _rule_based_reflection(
    explanation: str,
    knowledge_answer: str,
    symptoms: str,
    report: ReportStructure,
) -> ReflectionResult:
    lower_explanation = explanation.lower()
    missing: list[str] = []

    if not knowledge_answer.strip():
        missing.append("grounded knowledge")
    if report.diagnosis and report.diagnosis.lower() not in lower_explanation:
        diagnosis_token = report.diagnosis.lower().split()[0]
        if diagnosis_token not in lower_explanation:
            missing.append("report diagnosis")

    symptom_tokens = [t for t in symptoms.lower().split() if len(t) > 4][:3]
    if symptom_tokens and not any(token in lower_explanation for token in symptom_tokens):
        missing.append("symptom connection")

    if len(explanation.strip()) < 60:
        missing.append("sufficient detail")

    confidence = "high"
    if len(missing) >= 2:
        confidence = "low"
    elif missing:
        confidence = "medium"

    follow_up = ""
    if confidence == "low":
        follow_up = (
            f"Connect patient symptoms ({symptoms[:120]}) to report diagnosis "
            f"{report.diagnosis} and findings {report.findings[:2]}"
        )

    return ReflectionResult(
        grounded=not missing or confidence != "low",
        confidence=confidence,
        missing_topics=missing,
        follow_up_query=follow_up,
    )


async def reflect_on_explanation(
    explanation: str,
    knowledge_answer: str,
    symptoms: str,
    report: ReportStructure,
    patient: PatientContext,
) -> ReflectionResult:
    fallback = _rule_based_reflection(explanation, knowledge_answer, symptoms, report)

    client = get_chat_client(fast=True)
    agent = client.as_agent(name="SelfReflectionCritic", instructions=REFLECTION_INSTRUCTIONS)
    prompt = f"""
Report diagnosis: {report.diagnosis}
Report findings: {report.findings}
Patient symptoms: {symptoms}
Language: {patient.language}

Grounded knowledge used:
{knowledge_answer[:1500]}

Generated explanation:
{explanation}
"""
    try:
        result = await run_agent(agent, prompt)
        data = _parse_json_response(result.text)
        confidence = str(data.get("confidence", fallback.confidence)).lower()
        if confidence not in CONFIDENCE_ORDER:
            confidence = fallback.confidence

        return ReflectionResult(
            grounded=bool(data.get("grounded", fallback.grounded)),
            confidence=confidence,
            missing_topics=[str(t) for t in data.get("missing_topics", fallback.missing_topics)],
            follow_up_query=str(data.get("follow_up_query", fallback.follow_up_query)),
        )
    except Exception as exc:
        logger.warning("SelfReflectionCritic failed, using rule-based reflection: %s", exc)
        return fallback


def needs_knowledge_retry(reflection: ReflectionResult) -> bool:
    return reflection.confidence == "low" and bool(reflection.follow_up_query.strip())
