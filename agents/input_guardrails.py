"""Step 238 — block PII patterns in user-supplied text before agent workflow."""

from __future__ import annotations

import re
from dataclasses import dataclass

SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
EMAIL_PATTERN = re.compile(
    r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
    re.IGNORECASE,
)
CARD_CANDIDATE = re.compile(r"(?:\d[ -]?){13,19}")

ALLOWED_EMAIL_DOMAINS = frozenset(
    {
        "example.com",
        "example.org",
        "demo.local",
        "synthetic.demo",
        "test.local",
    }
)


@dataclass(frozen=True)
class GuardrailResult:
    blocked: bool
    reasons: list[str]


class InputGuardrailError(ValueError):
    """Raised when user input contains blocked PII patterns."""

    def __init__(self, reasons: list[str]):
        self.reasons = reasons
        super().__init__(
            "Please use synthetic demo data only — do not paste real personal information."
        )


def _luhn_valid(number: str) -> bool:
    digits = [int(ch) for ch in number if ch.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse = digits[::-1]
    for index, digit in enumerate(reverse):
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def _find_ssn(text: str) -> bool:
    return bool(SSN_PATTERN.search(text))


def _find_email(text: str) -> bool:
    for match in EMAIL_PATTERN.finditer(text):
        domain = match.group(0).split("@", 1)[-1].lower()
        if domain not in ALLOWED_EMAIL_DOMAINS:
            return True
    return False


def _find_credit_card(text: str) -> bool:
    for match in CARD_CANDIDATE.finditer(text):
        raw = match.group(0)
        digits = re.sub(r"\D", "", raw)
        if 13 <= len(digits) <= 19 and _luhn_valid(digits):
            return True
    return False


def scan_text_for_pii(text: str) -> list[str]:
    """Return human-readable reasons when blocked patterns are found."""
    if not text or not str(text).strip():
        return []

    reasons: list[str] = []
    if _find_ssn(text):
        reasons.append("Social Security Number pattern detected")
    if _find_credit_card(text):
        reasons.append("Credit card number pattern detected")
    if _find_email(text):
        reasons.append("Personal email address detected")
    return reasons


def check_user_inputs(
    *,
    symptoms: str = "",
    report_text: str = "",
    clarification_answers: list[str] | None = None,
) -> GuardrailResult:
    """Scan symptoms, report, and clarification answers for blocked PII."""
    reasons: list[str] = []

    for label, value in (
        ("symptoms", symptoms),
        ("report", report_text),
    ):
        hits = scan_text_for_pii(value)
        for hit in hits:
            reasons.append(f"{label}: {hit}")

    for index, answer in enumerate(clarification_answers or [], start=1):
        for hit in scan_text_for_pii(answer):
            reasons.append(f"clarification {index}: {hit}")

    unique = list(dict.fromkeys(reasons))
    return GuardrailResult(blocked=bool(unique), reasons=unique)


def enforce_input_guardrails(
    *,
    symptoms: str = "",
    report_text: str = "",
    clarification_answers: list[str] | None = None,
) -> None:
    """Raise InputGuardrailError when blocked PII patterns are present."""
    result = check_user_inputs(
        symptoms=symptoms,
        report_text=report_text,
        clarification_answers=clarification_answers,
    )
    if result.blocked:
        raise InputGuardrailError(result.reasons)
