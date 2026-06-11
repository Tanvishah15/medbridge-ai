import logging

from agents.base import get_chat_client, run_agent
from agents.logging_config import log_agent_input, log_agent_output
from agents.prompts import EXPLANATION_AGENT_INSTRUCTIONS
from agents.utils import is_vague_symptom_message

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
    output_language: str = "English",
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
    vague_note = ""
    if is_vague_symptom_message(symptoms):
        vague_note = (
            "The patient message is vague. Explain the REPORT findings first "
            "(diagnosis, affected area, key findings). Do not focus only on "
            "'not feeling well' — link discomfort to the report (e.g. ear fluid, hearing)."
        )

    prompt = f"""
    Report summary: {report_summary}
    Grounded knowledge: {knowledge}
    Patient symptoms: {symptoms}
    Literacy level: {literacy_level}
    Output language: {output_language}
    {_literacy_guidance(literacy_level)}
    {vague_note}
    Write a clear, empathetic explanation in {output_language} only.
    Use report-based phrasing only — never "you have [diagnosis]".
    Connect symptoms to report findings when possible.
    Lead with what the report shows. Do not diagnose or prescribe.
    """
    result = await run_agent(agent, prompt)
    explanation = result.text
    log_agent_output(agent_name, explanation=explanation)
    return explanation
