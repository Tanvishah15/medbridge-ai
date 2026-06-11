import pytest

from agents.safety_agent import (
    _detect_unsafe_flags,
    _is_report_based_explanation,
    validate_response,
)


def test_you_have_been_given_is_not_flagged():
    text = "Continue the antibiotics you have been given by your doctor."
    assert _detect_unsafe_flags(text) == []


def test_you_have_diabetes_is_flagged():
    text = "You have diabetes and should change your diet."
    assert "direct diagnosis phrasing" in _detect_unsafe_flags(text)


def test_report_based_explanation_detected():
    text = "Your report shows fluid in the middle ear."
    assert _is_report_based_explanation(text) is True


@pytest.mark.asyncio
async def test_report_based_otitis_media_passes_without_llm():
    text = (
        "Your report shows Otitis Media. There is fluid in the middle ear and the eardrum "
        "looks inflamed. This may explain the discharge you described for 3 days. "
        "The report recommends a follow-up in 7 days and following your doctor's treatment plan. "
        "Return sooner if you develop fever or severe pain. "
        "This is educational information, not medical advice. Please consult your doctor."
    )
    result = await validate_response(text)
    assert result["safe"] is True
    assert result["issues"] == []
    assert "Otitis Media" in result["revised_response"]


@pytest.mark.asyncio
async def test_direct_diagnosis_still_blocked():
    result = await validate_response("You definitely have diabetes.")
    assert not result.get("safe", True)
