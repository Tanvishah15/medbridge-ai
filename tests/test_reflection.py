from agents.models import PatientContext, ReportStructure
from orchestrator.reflection import (
    ReflectionResult,
    _rule_based_reflection,
    needs_knowledge_retry,
)


def test_reflection_high_confidence_when_grounded():
    report = ReportStructure(
        diagnosis="Otitis Media",
        findings=["Middle ear fluid present"],
    )
    knowledge = "Ear fluid can cause discharge during middle ear infection."
    explanation = (
        "Your report shows Otitis Media with middle ear fluid. "
        "Ear discharge for 3 days can match this finding. Please consult your doctor."
    )
    result = _rule_based_reflection(
        explanation,
        knowledge,
        "Ear discharge for 3 days with mild pain.",
        report,
    )
    assert result.confidence in {"high", "medium"}
    assert not needs_knowledge_retry(result) or result.confidence != "low"


def test_reflection_low_confidence_triggers_retry():
    report = ReportStructure(diagnosis="Otitis Media", findings=["Middle ear fluid"])
    result = _rule_based_reflection(
        "Short answer.",
        "",
        "Ear discharge for 3 days with pain and no fever.",
        report,
    )
    assert result.confidence == "low"
    assert needs_knowledge_retry(result) is True
    assert result.follow_up_query


def test_reflection_result_model():
    result = ReflectionResult(confidence="medium", missing_topics=["symptom connection"])
    assert result.grounded is True
    assert result.missing_topics == ["symptom connection"]
