from agents.base import get_chat_client
from agents.prompts import EXPLANATION_AGENT_INSTRUCTIONS


async def generate_explanation(
    report_summary: str,
    knowledge: str,
    symptoms: str,
    literacy_level: str = "simple",
) -> str:
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
    return (await agent.run(prompt)).text
