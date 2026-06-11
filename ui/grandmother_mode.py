"""Step 219 — one-click family / grandmother explanation mode."""

GRANDMOTHER_SUFFIX = "Explain this in very simple words for my grandmother."


def apply_grandmother_mode(current_symptoms: str = "") -> dict[str, str]:
    """Return sidebar settings for warm, family-friendly grandmother summaries."""
    symptoms = current_symptoms.strip()
    lower = symptoms.lower()
    if "grandmother" not in lower and "grandma" not in lower and "dadi" not in lower:
        symptoms = f"{symptoms}\n{GRANDMOTHER_SUFFIX}".strip() if symptoms else GRANDMOTHER_SUFFIX

    return {
        "audience": "family",
        "literacy_level": "simple",
        "symptoms": symptoms,
    }
