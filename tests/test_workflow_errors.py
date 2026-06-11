import asyncio

import pytest

from agents.models import PatientContext
from orchestrator.errors import friendly_error_message
from orchestrator.workflow import run_medbridge_safe


def test_friendly_error_message_value_error():
    msg = friendly_error_message(ValueError("Please provide report text or upload a synthetic demo report file."))
    assert "paste or upload" in msg.lower()


def test_friendly_error_message_timeout():
    msg = friendly_error_message(asyncio.TimeoutError())
    assert "timed out" in msg.lower()


@pytest.mark.asyncio
async def test_run_medbridge_safe_missing_report():
    patient = PatientContext(symptoms="Explain my report please.")
    result = await run_medbridge_safe("", patient)

    assert result.error is True
    assert result.error_message
    assert result.explanation == ""
    assert result.trace[0]["agent"] == "Error"


@pytest.mark.asyncio
async def test_run_medbridge_safe_invalid_session():
    patient = PatientContext(symptoms="Explain my report please.")
    result = await run_medbridge_safe(
        "Some report text that is long enough to pass validation.",
        patient,
        session_id="nonexistent-session-id",
    )

    assert result.error is True
    assert "session" in result.error_message.lower() or "checkpoint" in result.error_message.lower()
    assert result.trace[0]["agent"] == "Error"
