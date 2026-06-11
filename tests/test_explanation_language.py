from agents.explanation_agent import _audience_guidance, generate_explanation
from agents.prompts import EXPLANATION_AGENT_INSTRUCTIONS


def test_explanation_prompts_require_english_output():
    assert "Always write the explanation in English only" in EXPLANATION_AGENT_INSTRUCTIONS


def test_explanation_prompts_forbid_you_have_diagnosis():
    assert 'Never say "you have [condition]"' in EXPLANATION_AGENT_INSTRUCTIONS


def test_generate_explanation_accepts_output_language_param():
    assert "output_language" in generate_explanation.__code__.co_varnames


def test_generate_explanation_accepts_audience_param():
    assert "audience" in generate_explanation.__code__.co_varnames


def test_explanation_prompts_include_family_audience_mode():
    assert "family:" in EXPLANATION_AGENT_INSTRUCTIONS.lower()
    assert "grandmother" in EXPLANATION_AGENT_INSTRUCTIONS.lower()


def test_audience_guidance_family():
    guidance = _audience_guidance("family")
    assert "grandmother" in guidance.lower()


def test_audience_guidance_patient():
    guidance = _audience_guidance("patient")
    assert "patient" in guidance.lower()
