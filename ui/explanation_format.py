"""Format explanation text for Streamlit display (Step 229 polish)."""

import re

from agents.multilingual_agent import DEFAULT_DISCLAIMER

_ENGLISH_DISCLAIMER_TAIL = re.compile(
    r"\n+\s*Disclaimer:\s*This is educational information.*$",
    re.I | re.S,
)


def strip_trailing_english_disclaimer(text: str, language: str) -> str:
    """Remove appended English disclaimer when output is in another language."""
    if not text or language.strip().lower() == "english":
        return text

    trimmed = text.rstrip()
    default = DEFAULT_DISCLAIMER.strip()
    if trimmed.endswith(default):
        return trimmed[: -len(default)].rstrip()

    return _ENGLISH_DISCLAIMER_TAIL.sub("", text).strip()
