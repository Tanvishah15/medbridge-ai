import json
import logging
import re

from agents.base import get_chat_client
from agents.logging_config import log_agent_input, log_agent_output
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
    agent_name = "ClarificationAgent"
    log_agent_input(
        agent_name,
        diagnosis=report.diagnosis,
        findings=report.findings,
        symptoms=patient.symptoms,
        language=patient.language,
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
        log_agent_output(agent_name, questions=questions)
        return questions
    except Exception:
        logger.warning("%s | JSON parse failed, using raw text", agent_name)
        questions = [result.text]
        log_agent_output(agent_name, questions=questions)
        return questions
