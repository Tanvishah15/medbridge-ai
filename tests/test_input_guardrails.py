"""Step 238 — input guardrail tests."""

import pytest

from agents.input_guardrails import (
    InputGuardrailError,
    check_user_inputs,
    enforce_input_guardrails,
    scan_text_for_pii,
)
from agents.models import PatientContext
from orchestrator.errors import friendly_error_message
from orchestrator.workflow import run_medbridge_safe


def test_scan_ssn_pattern():
    assert "Social Security Number" in scan_text_for_pii("My SSN is 123-45-6789 please help")[0]


def test_scan_credit_card_pattern():
    reasons = scan_text_for_pii("Payment card 4111 1111 1111 1111 on file")
    assert any("Credit card" in reason for reason in reasons)


def test_scan_email_blocks_real_domains():
    assert "Personal email" in scan_text_for_pii("Contact me at patient@gmail.com")[0]


def test_scan_email_allows_demo_domains():
    assert scan_text_for_pii("Demo contact: user@example.com") == []


def test_clean_synthetic_text_passes():
    assert scan_text_for_pii("Ear pain for 3 days with fluid discharge.") == []


def test_check_user_inputs_combines_fields():
    result = check_user_inputs(
        symptoms="123-45-6789",
        report_text="4111 1111 1111 1111",
        clarification_answers=["reach me at real.person@yahoo.com"],
    )
    assert result.blocked
    assert len(result.reasons) == 3


def test_enforce_raises_with_reasons():
    with pytest.raises(InputGuardrailError) as exc_info:
        enforce_input_guardrails(symptoms="Email: secret@outlook.com")
    assert exc_info.value.reasons
    assert "synthetic demo data" in str(exc_info.value).lower()


def test_friendly_error_message_guardrail():
    msg = friendly_error_message(InputGuardrailError(["symptoms: Personal email address detected"]))
    assert "synthetic demo data" in msg.lower()
    assert "email" in msg.lower()


@pytest.mark.asyncio
async def test_run_medbridge_safe_blocks_pii():
    patient = PatientContext(symptoms="My SSN is 999-88-7777")
    result = await run_medbridge_safe(
        "Synthetic ENT report with enough text for validation.",
        patient,
    )
    assert result.error is True
    assert "synthetic demo data" in result.error_message.lower()
    assert result.trace[0]["agent"] == "Error"
