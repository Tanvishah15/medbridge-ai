"""Step 239 — output guardrail tests."""

import pytest

from agents.output_guardrails import (
    _append_disclaimer,
    apply_output_guardrails,
    redact_output_pii,
)


def test_redact_ssn_from_output():
    text = "Patient ID 123-45-6789 was noted in the chart."
    redacted, issues = redact_output_pii(text)
    assert "123-45-6789" not in redacted
    assert "[REDACTED]" in redacted
    assert issues


def test_redact_credit_card_from_output():
    text = "Card on file: 4111 1111 1111 1111"
    redacted, issues = redact_output_pii(text)
    assert "4111" not in redacted
    assert "[REDACTED]" in redacted
    assert issues


def test_redact_email_keeps_demo_domain():
    text = "Contact demo@example.com for follow-up."
    redacted, issues = redact_output_pii(text)
    assert "demo@example.com" in redacted
    assert issues == []


def test_redact_real_email():
    text = "Email the clinic at patient@gmail.com"
    redacted, issues = redact_output_pii(text)
    assert "patient@gmail.com" not in redacted
    assert "[REDACTED]" in redacted


def test_append_disclaimer_when_missing():
    result = _append_disclaimer("Your report shows fluid in the ear.")
    assert "consult your doctor" in result.lower()
    assert "not medical advice" in result.lower()


def test_append_disclaimer_skips_when_present():
    text = "Your report shows findings. Please consult your doctor."
    assert _append_disclaimer(text) == text


def test_apply_redacts_echoed_pii_and_adds_disclaimer():
    result = apply_output_guardrails(
        "Your chart lists SSN 123-45-6789 for verification.",
        safety_passed=True,
    )
    assert "123-45-6789" not in result.text
    assert result.redacted is True
    assert result.passed is True
    assert "consult your doctor" in result.text.lower()


def test_apply_passes_clean_report_explanation():
    text = (
        "Your report shows Otitis Media with middle ear fluid. "
        "Follow your doctor's treatment plan."
    )
    result = apply_output_guardrails(text, safety_passed=True)
    assert result.passed is True
    assert "Otitis Media" in result.text
    assert "consult your doctor" in result.text.lower()


def test_apply_preserves_safety_issues():
    result = apply_output_guardrails(
        "Your report shows findings.",
        safety_passed=False,
        safety_issues=["dosage specified"],
    )
    assert result.passed is False
    assert "dosage specified" in result.issues
