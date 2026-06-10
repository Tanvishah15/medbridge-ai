import logging

from agents.base import get_chat_client
from agents.logging_config import log_agent_input, log_agent_output
from agents.prompts import MULTILINGUAL_AGENT_INSTRUCTIONS

logger = logging.getLogger(__name__)


async def translate_explanation(
    explanation: str,
    target_language: str,
    audience: str = "patient",
) -> str:
    agent_name = "MultilingualAgent"
    log_agent_input(
        agent_name,
        explanation=explanation,
        target_language=target_language,
        audience=audience,
    )
    client = get_chat_client()
    agent = client.as_agent(
        name="MultilingualAgent",
        instructions=MULTILINGUAL_AGENT_INSTRUCTIONS,
    )
    prompt = f"""
    Translate and adapt this explanation to {target_language}.
    Audience: {audience}
    Include disclaimer in {target_language}.

    Explanation:
    {explanation}
    """
    translated = (await agent.run(prompt)).text
    log_agent_output(agent_name, translated=translated)
    return translated
