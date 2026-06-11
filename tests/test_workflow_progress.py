import pytest

from orchestrator.workflow import _notify_progress, run_medbridge
from agents.models import PatientContext


@pytest.mark.asyncio
async def test_run_medbridge_emits_progress_callbacks(monkeypatch):
    seen: list[str] = []

    async def fake_parse_report(_text: str):
        from agents.models import ReportStructure

        return ReportStructure(
            diagnosis="Demo",
            findings=["finding"],
            affected_area="ear",
            recommendations=["follow up"],
        )

    async def fake_plan(*_args, **_kwargs):
        from orchestrator.planner import WorkflowPlan

        return WorkflowPlan(
            needs_clarification=False,
            knowledge_queries=["demo query"],
            use_multilingual=False,
            rationale="test",
        )

    async def fake_questions(*_args, **_kwargs):
        return []

    async def fake_knowledge(*_args, **_kwargs):
        return {"answer": "Grounded demo knowledge.", "citations": []}

    async def fake_explanation(*_args, **_kwargs):
        return "Your report shows demo findings. Please consult your doctor."

    async def fake_reflect(*_args, **_kwargs):
        from orchestrator.reflection import ReflectionResult

        return ReflectionResult(grounded=True, confidence="high", missing_topics=[], follow_up_query="")

    async def fake_safety(text: str):
        return {"safe": True, "issues": [], "revised_response": text}

    monkeypatch.setattr("orchestrator.workflow.parse_report", fake_parse_report)
    monkeypatch.setattr("orchestrator.workflow.plan_workflow", fake_plan)
    monkeypatch.setattr("orchestrator.workflow.get_clarification_questions", fake_questions)
    monkeypatch.setattr("orchestrator.workflow.retrieve_medical_knowledge", fake_knowledge)
    monkeypatch.setattr("orchestrator.workflow.generate_explanation", fake_explanation)
    monkeypatch.setattr("orchestrator.workflow.reflect_on_explanation", fake_reflect)
    monkeypatch.setattr("orchestrator.workflow.validate_response", fake_safety)

    patient = PatientContext(symptoms="ear pain 2 days", language="English")
    await run_medbridge("SYNTHETIC REPORT TEXT", patient, progress_callback=seen.append)

    assert seen == [
        "reading_report",
        "checking_symptoms",
        "retrieving_knowledge",
        "explaining",
        "validating_safety",
    ]


def test_notify_progress_no_callback():
    _notify_progress(None, "explaining")
