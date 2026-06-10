import logging

from agents.base import get_chat_client
from agents.prompts import MULTILINGUAL_AGENT_INSTRUCTIONS

logger = logging.getLogger(__name__)


async def translate_explanation(
    explanation: str,
    target_language: str,
    audience: str = "patient",
) -> str:
    logger.info(
        "MultilingualAgent: target=%s audience=%s input_chars=%d",
        target_language,
        audience,
        len(explanation),
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
    logger.info("MultilingualAgent: output %d chars", len(translated))
    return translated
