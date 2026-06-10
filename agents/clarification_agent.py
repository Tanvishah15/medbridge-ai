import json
import logging
import re

from agents.base import get_chat_client
from agents.models import PatientContext, ReportStructure
from agents.prompts import CLARIFICATION_AGENT_INSTRUCTIONS

logger = logging.getLogger(__name__)


def _parse_json_list(text: str) -> list:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    data = json.loads(text)
    if isinstance(data, list):
        return [str(item) for item in data]
    if isinstance(data, dict) and "questions" in data:
        return [str(q) for q in data["questions"]]
    return [str(data)]


async def get_clarification_questions(
    report: ReportStructure,
    patient: PatientContext,
) -> list[str]:
    logger.info(
        "ClarificationAgent: language=%s symptoms=%r",
        patient.language,
        patient.symptoms[:120],
    )
    client = get_chat_client()
    agent = client.as_agent(
        name="ClarificationAgent",
        instructions=CLARIFICATION_AGENT_INSTRUCTIONS,
    )
    prompt = f"""
    Report: {report.model_dump_json()}
    Patient message: {patient.symptoms}
    Language: {patient.language}
    Return JSON list of 1-3 questions.
    """
    result = await agent.run(prompt)
    try:
        questions = _parse_json_list(result.text)
        logger.info("ClarificationAgent: generated %d questions", len(questions))
        return questions
    except Exception:
        logger.warning("ClarificationAgent: JSON parse failed, using raw text")
        return [result.text]
