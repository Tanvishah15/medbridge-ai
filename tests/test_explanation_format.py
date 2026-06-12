from agents.multilingual_agent import DEFAULT_DISCLAIMER
from ui.explanation_format import strip_trailing_english_disclaimer


def test_strip_english_disclaimer_from_hindi_output():
    hindi = "आपके कान में infection है। कृपया डॉक्टर से मिलें।"
    text = hindi + DEFAULT_DISCLAIMER
    cleaned = strip_trailing_english_disclaimer(text, "Hindi")
    assert cleaned == hindi
    assert "Disclaimer: This is educational" not in cleaned


def test_keep_english_disclaimer_for_english():
    text = "Your ear has fluid." + DEFAULT_DISCLAIMER
    assert strip_trailing_english_disclaimer(text, "English") == text


def test_strip_regex_fallback_for_english_tail():
    text = "Resumen en español.\n\nDisclaimer: This is educational information, not medical advice."
    cleaned = strip_trailing_english_disclaimer(text, "Spanish")
    assert cleaned == "Resumen en español."
