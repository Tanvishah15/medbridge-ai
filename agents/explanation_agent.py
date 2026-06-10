import logging

from agents.base import get_chat_client
from agents.prompts import EXPLANATION_AGENT_INSTRUCTIONS

logger = logging.getLogger(__name__)


async def generate_explanation(
    report_summary: str,
    knowledge: str,
    symptoms: str,
    literacy_level: str = "simple",
) -> str:
    logger.info(
        "PatientExplanationAgent: literacy=%s symptoms=%r",
        literacy_level,
        symptoms[:120],
    )
    client = get_chat_client()
    agent = client.as_agent(
        name="PatientExplanationAgent",
        instructions=EXPLANATION_AGENT_INSTRUCTIONS,
    )
    prompt = f"""
    Report summary: {report_summary}
    Grounded knowledge: {knowledge}
    Patient symptoms: {symptoms}
    Literacy level: {literacy_level}
    Write a clear, empathetic explanation. Connect symptoms to findings.
    """
    explanation = (await agent.run(prompt)).text
    logger.info("PatientExplanationAgent: generated %d chars", len(explanation))
    return explanation
