"""Step 241 — language parity tests (Hindi, Spanish, Arabic equal quality)."""

import json
from pathlib import Path

import pytest

from agents.models import MedBridgeResponse
from tests.language_parity import (
    MIN_CASE_SCORE_PCT,
    MIN_EXPLANATION_LENGTH,
    PARITY_CASE_IDS,
    PARITY_LANGUAGES,
    check_parity_quality,
    compare_parity_suite,
)
from tests.run_eval import CaseResult, evaluate_case, score_result

EVAL_FILE = Path(__file__).resolve().parent / "eval_cases.json"


@pytest.fixture
def eval_cases():
    return json.loads(EVAL_FILE.read_text(encoding="utf-8"))


def test_step241_parity_cases_cover_hindi_spanish_arabic(eval_cases):
    by_id = {case["id"]: case for case in eval_cases["cases"]}
    for case_id in PARITY_CASE_IDS:
        assert case_id in by_id
        lang = by_id[case_id]["patient"]["language"]
        assert lang == PARITY_LANGUAGES[case_id]


def test_step241_parity_cases_require_multilingual_criterion(eval_cases):
    by_id = {case["id"]: case for case in eval_cases["cases"]}
    for case_id in PARITY_CASE_IDS:
        criteria = by_id[case_id]["expects"].get("criteria", {})
        assert criteria.get("multilingual") is True
        assert criteria.get("safety") is True
        assert criteria.get("grounding") is True


def test_step241_parity_same_explanation_length_bar():
    by_id = {
        case["id"]: case
        for case in json.loads(EVAL_FILE.read_text(encoding="utf-8"))["cases"]
    }
    lengths = [
        by_id[case_id]["expects"].get("explanation_min_length", MIN_EXPLANATION_LENGTH)
        for case_id in PARITY_CASE_IDS
    ]
    assert min(lengths) >= MIN_EXPLANATION_LENGTH
    assert max(lengths) - min(lengths) <= 10


def test_check_parity_quality_rejects_english_only_hindi():
    case = {
        "expects": {
            "language": "hindi",
            "safety_passed": True,
            "grounding": {"citations_or_doctor": True},
        }
    }
    result = MedBridgeResponse(
        explanation="Your report shows otitis media. Please consult your doctor.",
        safety_passed=True,
        trace=[{"agent": "Multilingual", "output": {}}],
    )
    passed, failures = check_parity_quality(result, case)
    assert passed is False
    assert failures


def test_check_parity_quality_accepts_hindi_output():
    case = {
        "expects": {
            "language": "hindi",
            "safety_passed": True,
            "grounding": {"citations_or_doctor": True},
        }
    }
    result = MedBridgeResponse(
        explanation=(
            "आपकी रिपोर्ट में कान की समस्या दिखाई देती है। "
            "कृपया अपने डॉक्टर से मिलें।"
        ),
        safety_passed=True,
        trace=[{"agent": "Multilingual", "output": {}}],
    )
    passed, failures = check_parity_quality(result, case)
    assert passed is True
    assert failures == []


def test_compare_parity_suite_flags_large_gap():
    results = [
        CaseResult("eval_002", "Hindi", True, 100.0, {}, [], 1.0),
        CaseResult("eval_003", "Spanish", True, 100.0, {}, [], 1.0),
        CaseResult("eval_004", "Arabic", False, 40.0, {}, ["language"], 1.0),
    ]
    passed, failures = compare_parity_suite(results)
    assert passed is False
    assert any("gap" in item.lower() or "eval_004" in item for item in failures)


def test_compare_parity_suite_passes_balanced_scores():
    results = [
        CaseResult(case_id, PARITY_LANGUAGES[case_id], True, 100.0, {}, [], 1.0)
        for case_id in PARITY_CASE_IDS
    ]
    passed, failures = compare_parity_suite(results)
    assert passed is True
    assert failures == []


def test_parity_eval_cases_score_multilingual_criterion():
    hindi = MedBridgeResponse(
        explanation="आपके कान में infection है। डॉक्टर से consult करें।",
        safety_passed=True,
    )
    scores, failures = score_result(
        hindi,
        {"language": "hindi", "criteria": {"multilingual": True}},
    )
    assert scores.get("multilingual") is True
    assert failures == []
