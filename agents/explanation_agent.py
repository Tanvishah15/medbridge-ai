import logging

from agents.base import get_chat_client, run_agent
from agents.logging_config import log_agent_input, log_agent_output
from agents.prompts import EXPLANATION_AGENT_INSTRUCTIONS

logger = logging.getLogger(__name__)


def _literacy_guidance(literacy_level: str) -> str:
    if literacy_level.lower() == "standard":
        return "Use standard literacy: clear paragraphs with moderate medical detail."
    return "Use simple literacy: very short sentences and everyday words only."


async def generate_explanation(
    report_summary: str,
    knowledge: str,
    symptoms: str,
    literacy_level: str = "simple",
) -> str:
    agent_name = "PatientExplanationAgent"
    log_agent_input(
        agent_name,
        report_summary=report_summary,
        knowledge=knowledge,
        symptoms=symptoms,
        literacy_level=literacy_level,
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
    {_literacy_guidance(literacy_level)}
    Write a clear, empathetic explanation. Connect symptoms to findings.
    Acknowledge how the patient may feel. Do not diagnose or prescribe.
    """
    result = await run_agent(agent, prompt)
    explanation = result.text
    log_agent_output(agent_name, explanation=explanation)
    return explanation
