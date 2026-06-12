"""Step 241 — cross-language quality parity (Hindi, Spanish, Arabic)."""

from __future__ import annotations

from agents.models import MedBridgeResponse

PARITY_CASE_IDS = ("eval_002", "eval_003", "eval_004")

PARITY_LANGUAGES = {
    "eval_002": "Hindi",
    "eval_003": "Spanish",
    "eval_004": "Arabic",
}

MIN_EXPLANATION_LENGTH = 50
MIN_CASE_SCORE_PCT = 80.0
MAX_SCORE_GAP_PCT = 25.0


def check_parity_quality(result: MedBridgeResponse, case: dict) -> tuple[bool, list[str]]:
    """Apply the same quality bar to each non-English demo language."""
    from agents.multilingual_agent import DEFAULT_DISCLAIMER
    from tests.run_eval import _check_grounding, _check_language, _trace_agents

    failures: list[str] = []
    expects = case.get("expects", {})
    language = expects.get("language", "")

    if result.error:
        failures.append(result.error_message or "Workflow returned error")

    explanation = result.explanation.strip()
    if len(explanation) < MIN_EXPLANATION_LENGTH:
        failures.append(
            f"Explanation shorter than parity minimum ({MIN_EXPLANATION_LENGTH} chars)"
        )

    if expects.get("safety_passed") is True and not result.safety_passed:
        failures.append("safety_passed is False")

    if language and language.lower() != "english":
        if "Multilingual" not in _trace_agents(result):
            failures.append("Missing Multilingual agent in trace")

        ok, reason = _check_language(explanation, language)
        if not ok:
            failures.append(reason or f"Language check failed for {language}")

        if DEFAULT_DISCLAIMER.strip() in result.explanation:
            failures.append("English-only disclaimer appended to non-English explanation")

    grounded, grounding_failures = _check_grounding(result, expects)
    if not grounded:
        failures.extend(grounding_failures)

    return len(failures) == 0, failures


def compare_parity_suite(case_results: list) -> tuple[bool, list[str]]:
    """Ensure Hindi, Spanish, and Arabic cases score within parity tolerance."""
    failures: list[str] = []
    if len(case_results) != len(PARITY_CASE_IDS):
        failures.append(
            f"Expected {len(PARITY_CASE_IDS)} parity cases, got {len(case_results)}"
        )
        return False, failures

    scores = [item.score_pct for item in case_results]
    gap = max(scores) - min(scores)
    if gap > MAX_SCORE_GAP_PCT:
        failures.append(
            f"Score gap {gap:.1f}% exceeds {MAX_SCORE_GAP_PCT}% parity tolerance"
        )

    for item in case_results:
        if item.score_pct < MIN_CASE_SCORE_PCT:
            failures.append(
                f"{item.case_id} ({PARITY_LANGUAGES.get(item.case_id, '?')}) "
                f"below {MIN_CASE_SCORE_PCT}% bar ({item.score_pct}%)"
            )
        if not item.passed:
            failures.append(f"{item.case_id} failed: {'; '.join(item.failures)}")

    return len(failures) == 0, failures
