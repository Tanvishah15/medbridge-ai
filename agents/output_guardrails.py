"""Step 239 — post-safety output guardrails (defense in depth after Safety Agent)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from agents.input_guardrails import (
    ALLOWED_EMAIL_DOMAINS,
    CARD_CANDIDATE,
    EMAIL_PATTERN,
    SSN_PATTERN,
    scan_text_for_pii,
    _luhn_valid,
)

DISCLAIMER_MARKERS = (
    "consult your doctor",
    "consult a doctor",
    "healthcare professional",
    "not medical advice",
    "educational information",
)

STANDARD_DISCLAIMER = (
    "This is educational information, not medical advice. Please consult your doctor."
)


@dataclass(frozen=True)
class OutputGuardrailResult:
    text: str
    passed: bool
    issues: list[str]
    redacted: bool


def _has_disclaimer(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in DISCLAIMER_MARKERS)


def _append_disclaimer(text: str) -> str:
    stripped = text.rstrip()
    if not stripped or _has_disclaimer(stripped):
        return stripped
    return f"{stripped}\n\n{STANDARD_DISCLAIMER}"


def _redact_credit_cards(text: str) -> str:
    result = text
    for match in reversed(list(CARD_CANDIDATE.finditer(text))):
        raw = match.group(0)
        digits = re.sub(r"\D", "", raw)
        if 13 <= len(digits) <= 19 and _luhn_valid(digits):
            result = result[: match.start()] + "[REDACTED]" + result[match.end() :]
    return result


def _redact_emails(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        domain = match.group(0).split("@", 1)[-1].lower()
        if domain in ALLOWED_EMAIL_DOMAINS:
            return match.group(0)
        return "[REDACTED]"

    return EMAIL_PATTERN.sub(replace, text)


def redact_output_pii(text: str) -> tuple[str, list[str]]:
    """Strip PII patterns from model output before display."""
    issues = scan_text_for_pii(text)
    if not issues:
        return text, []

    redacted = SSN_PATTERN.sub("[REDACTED]", text)
    redacted = _redact_credit_cards(redacted)
    redacted = _redact_emails(redacted)
    return redacted, [f"output redacted: {issue}" for issue in issues]


def apply_output_guardrails(
    text: str,
    *,
    safety_passed: bool = True,
    safety_issues: list[str] | None = None,
) -> OutputGuardrailResult:
    """Finalize explanation after Safety Agent — PII redaction + disclaimer only."""
    if not text or not str(text).strip():
        return OutputGuardrailResult(text=text, passed=safety_passed, issues=[], redacted=False)

    issues: list[str] = list(safety_issues or [])
    working, pii_issues = redact_output_pii(text)
    issues.extend(pii_issues)
    working = _append_disclaimer(working)

    unique_issues = list(dict.fromkeys(issues))
    return OutputGuardrailResult(
        text=working,
        passed=safety_passed,
        issues=unique_issues,
        redacted=bool(pii_issues),
    )
