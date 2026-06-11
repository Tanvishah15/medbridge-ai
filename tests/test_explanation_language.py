from agents.explanation_agent import generate_explanation
from agents.prompts import EXPLANATION_AGENT_INSTRUCTIONS


def test_explanation_prompts_require_english_output():
    assert "Always write the explanation in English only" in EXPLANATION_AGENT_INSTRUCTIONS


def test_generate_explanation_accepts_output_language_param():
    assert "output_language" in generate_explanation.__code__.co_varnames
