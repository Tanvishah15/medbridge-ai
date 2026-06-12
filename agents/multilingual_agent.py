import logging

from agents.base import get_chat_client, run_agent
from agents.logging_config import log_agent_input, log_agent_output
from agents.prompts import MULTILINGUAL_AGENT_INSTRUCTIONS
from agents.utils import has_disclaimer

logger = logging.getLogger(__name__)

DEFAULT_DISCLAIMER = (
    "\n\nDisclaimer: This is educational information, not medical advice. "
    "Please consult your doctor or healthcare provider."
)

LANGUAGE_FALLBACK_DISCLAIMERS = {
    "hindi": (
        "\n\nअस्वीकरण: यह शैक्षिक जानकारी है, चिकित्सा सलाह नहीं। "
        "कृपया अपने डॉक्टर से परामर्श करें।"
    ),
    "spanish": (
        "\n\nAviso: Esta información es educativa, no es consejo médico. "
        "Consulte a su médico."
    ),
    "arabic": (
        "\n\nتنبيه: هذه معلومات تعليمية وليست نصيحة طبية. "
        "يرجى استشارة طبيبك."
    ),
}


def _fallback_disclaimer(target_language: str) -> str:
    return LANGUAGE_FALLBACK_DISCLAIMERS.get(target_language.lower(), DEFAULT_DISCLAIMER)


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
    client = get_chat_client(fast=True)
    agent = client.as_agent(
        name="MultilingualAgent",
        instructions=MULTILINGUAL_AGENT_INSTRUCTIONS,
    )
    audience_note = ""
    if audience.lower() == "family":
        audience_note = "Adapt for a family member explaining to an elderly relative (warm, simple tone)."

    prompt = f"""
    Translate and adapt this explanation to {target_language}.
    Audience: {audience}
    {audience_note}
    Preserve correct medical anatomy in {target_language} (e.g. middle ear ≠ temple/forehead).
    REQUIRED: End with a disclaimer in {target_language} that this is not medical advice.

    Explanation:
    {explanation}
    """
    result = await run_agent(agent, prompt)
    translated = result.text
    if not has_disclaimer(translated):
        logger.warning("%s | Disclaimer missing — appending fallback", agent_name)
        translated = translated.rstrip() + _fallback_disclaimer(target_language)

    log_agent_output(agent_name, translated=translated)
    return translated
