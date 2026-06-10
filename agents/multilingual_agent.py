from agents.base import get_chat_client
from agents.prompts import MULTILINGUAL_AGENT_INSTRUCTIONS


async def translate_explanation(
    explanation: str,
    target_language: str,
    audience: str = "patient",
) -> str:
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
    return (await agent.run(prompt)).text
