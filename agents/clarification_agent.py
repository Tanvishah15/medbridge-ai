import json
import logging
import re

from agents.base import get_chat_client, run_agent
from agents.logging_config import log_agent_input, log_agent_output
from agents.models import PatientContext, ReportStructure
from agents.prompts import CLARIFICATION_AGENT_INSTRUCTIONS
from agents.utils import symptoms_are_complete

logger = logging.getLogger(__name__)

MAX_CLARIFICATION_QUESTIONS = 3


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
    agent_name = "ClarificationAgent"
    log_agent_input(
        agent_name,
        diagnosis=report.diagnosis,
        findings=report.findings,
        symptoms=patient.symptoms,
        language=patient.language,
    )

    if symptoms_are_complete(patient.symptoms):
        logger.info("%s | Symptoms complete — skipping clarification", agent_name)
        log_agent_output(agent_name, questions=[])
        return []

    client = get_chat_client(fast=True)
    agent = client.as_agent(
        name="ClarificationAgent",
        instructions=CLARIFICATION_AGENT_INSTRUCTIONS,
    )
    prompt = f"""
    Report: {report.model_dump_json()}
    Patient message: {patient.symptoms}
    Language: {patient.language}
    Return JSON list of 0-3 questions. Never more than 3.
    """
    try:
        result = await run_agent(agent, prompt)
    except Exception as exc:
        logger.warning("%s | LLM call failed: %s", agent_name, exc)
        log_agent_output(agent_name, questions=[])
        return []

    try:
        questions = _parse_json_list(result.text)[:MAX_CLARIFICATION_QUESTIONS]
    except Exception:
        logger.warning("%s | JSON parse failed, using raw text", agent_name)
        questions = [result.text][:MAX_CLARIFICATION_QUESTIONS]

    log_agent_output(agent_name, questions=questions)
    return questions
