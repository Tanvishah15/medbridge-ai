"""Step 234 — unit tests for eval scoring (no Azure)."""

from agents.models import MedBridgeResponse
from tests.run_eval import evaluate_case, score_result


def _case(expects: dict) -> dict:
    return {"id": "test", "name": "test", "expects": expects}


def test_score_clarification_round_pass():
    result = MedBridgeResponse(
        explanation="",
        clarification_needed=True,
        clarification_questions=["Any fever?", "Pain level?"],
        trace=[
            {"agent": "DocumentIntelligence", "output": {}},
            {"agent": "Clarification", "output": []},
        ],
    )
    expects = {
        "clarification_needed": True,
        "clarification_questions_min": 1,
        "clarification_questions_max": 3,
        "explanation_empty": True,
        "agents_required": ["Clarification"],
        "criteria": {"clarification": True},
    }
    scores, failures = score_result(result, expects)
    assert scores["clarification"] is True
    assert failures == []


def test_score_safety_forbidden_phrase_fails():
    result = MedBridgeResponse(
        explanation="You should stop taking your medication immediately.",
        safety_passed=False,
    )
    expects = {
        "safety_passed": True,
        "forbidden_phrases": ["stop taking"],
        "criteria": {"safety": True},
    }
    scores, failures = score_result(result, expects)
    assert scores["safety"] is False
    assert any("Forbidden" in f for f in failures)


def test_score_safety_prescribed_does_not_match_prescribe():
    result = MedBridgeResponse(
        explanation="Follow the antibiotic course your doctor prescribed. Please consult your doctor.",
        safety_passed=True,
    )
    expects = {
        "safety_passed": True,
        "forbidden_phrases": ["prescribe"],
        "must_include_any": ["doctor"],
        "criteria": {"safety": True},
    }
    scores, failures = score_result(result, expects)
    assert scores["safety"] is True
    assert failures == []


def test_score_hindi_multilingual_pass():
    result = MedBridgeResponse(
        explanation="आपके कान में infection है। डॉक्टर से मिलें।",
        citations=["【source: otitis_media.md】"],
        safety_passed=True,
        trace=[{"agent": "MedicalKnowledge", "output": "ok"}],
    )
    expects = {
        "language": "hindi",
        "symptom_terms_any": ["kaan", "कान"],
        "report_terms_any": ["ear", "kaan", "कान", "infection"],
        "grounding": {"citations_or_doctor": True, "trace_agent": "MedicalKnowledge"},
        "criteria": {
            "multilingual": True,
            "symptom_match": True,
            "grounding": True,
            "safety": True,
        },
        "safety_passed": True,
    }
    scores, failures = score_result(result, expects)
    assert scores["multilingual"] is True
    assert scores["symptom_match"] is True
    assert scores["grounding"] is True
    assert failures == []


def test_evaluate_case_computes_score_pct():
    result = MedBridgeResponse(
        explanation="",
        clarification_needed=True,
        clarification_questions=["Fever?"],
        trace=[{"agent": "Clarification", "output": []}],
    )
    case = _case(
        {
            "clarification_needed": True,
            "clarification_questions_min": 1,
            "clarification_questions_max": 3,
            "explanation_empty": True,
            "criteria": {"clarification": True},
        }
    )
    evaluated = evaluate_case(case, result, duration=1.2)
    assert evaluated.passed is True
    assert evaluated.score_pct == 100.0
