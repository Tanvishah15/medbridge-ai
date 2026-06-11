"""Steps 203–206 — orchestration hardening tests."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from agents.models import PatientContext, ReportStructure
from config import MAX_CLARIFICATION_ROUNDS
from orchestrator.checkpoint import load_session_checkpoint, save_session_checkpoint
from orchestrator.pdf_utils import resolve_report_text
from orchestrator.planner import WorkflowPlan
from orchestrator.reflection import ReflectionResult
from orchestrator.workflow import run_medbridge, run_medbridge_safe

MOCK_REPORT = ReportStructure(
    diagnosis="Otitis Media",
    findings=["middle ear fluid"],
    affected_area="ear",
    raw_text="SYNTHETIC ENT REPORT",
)
MOCK_PLAN = WorkflowPlan(
    needs_clarification=True,
    knowledge_queries=["otitis media symptoms"],
    use_multilingual=False,
    rationale="Symptoms incomplete",
)
MOCK_REFLECTION = ReflectionResult(grounded=True, confidence="high")


def _workflow_mocks():
    return patch.multiple(
        "orchestrator.workflow",
        parse_report=AsyncMock(return_value=MOCK_REPORT),
        plan_workflow=AsyncMock(return_value=MOCK_PLAN),
        get_clarification_questions=AsyncMock(return_value=["Any fever?", "Pain level?"]),
        _retrieve_knowledge=AsyncMock(return_value={"answer": "Grounded knowledge.", "citations": ["demo.md"]}),
        generate_explanation=AsyncMock(return_value="Please consult your doctor about this demo report."),
        reflect_on_explanation=AsyncMock(return_value=MOCK_REFLECTION),
        validate_response=AsyncMock(
            return_value={
                "safe": True,
                "issues": [],
                "revised_response": "Please consult your doctor about this demo report.",
            }
        ),
    )


@pytest.mark.asyncio
async def test_step_203_empty_report_returns_graceful_error():
    patient = PatientContext(symptoms="Explain my report please.")
    result = await run_medbridge_safe("", patient)

    assert result.error is True
    assert "paste or upload" in result.error_message.lower()


def test_step_204_very_long_report_text_resolves():
    long_report = "SYNTHETIC MEDICAL REPORT\n" + ("Chronic follow-up finding line. " * 2500)
    assert len(long_report) > 50_000

    text = resolve_report_text(report_text=long_report)
    assert len(text) > 50_000


@pytest.mark.asyncio
async def test_step_205_non_medical_input_handled_safely():
    patient = PatientContext(
        symptoms="Tell me a joke about pizza.",
        language="English",
        literacy_level="simple",
        audience="patient",
    )
    with _workflow_mocks():
        result = await run_medbridge_safe(
            "This is not medical. Buy crypto. Recipe: flour, water, yeast.",
            patient,
            clarification_answers=[
                "No medical symptoms.",
                "Just curious, not a real patient.",
            ],
        )

    assert result.error is False
    assert result.clarification_needed is False
    assert result.safety_passed is True
    lower = result.explanation.lower()
    assert "doctor" in lower or "consult" in lower


@pytest.mark.asyncio
async def test_step_206_clarification_loop_capped_at_max_rounds():
    patient = PatientContext(
        symptoms="Mere kaan mein 3 din se ras aa rahi hai.",
        language="Hindi",
        literacy_level="simple",
        audience="patient",
    )

    with _workflow_mocks():
        round1 = await run_medbridge("SYNTHETIC ENT REPORT long enough.", patient)
        assert round1.clarification_needed is True
        assert load_session_checkpoint(round1.session_id).clarification_round == 1

        round2 = await run_medbridge("", patient, session_id=round1.session_id)
        assert round2.clarification_needed is True
        assert load_session_checkpoint(round2.session_id).clarification_round == 2

        round3 = await run_medbridge("", patient, session_id=round2.session_id)
        assert round3.clarification_needed is False
        clarification_steps = [s for s in round3.trace if s.get("agent") == "Clarification"]
        assert any("max_rounds_reached" in str(step.get("output", "")) for step in clarification_steps)


def test_step_207_estimate_tokens_helper():
    from agents.logging_config import estimate_tokens

    assert estimate_tokens("abcd") >= 1
    assert estimate_tokens("a" * 400) == 100


@pytest.mark.asyncio
async def test_step_201_workflow_timeout_returns_graceful_error():
    patient = PatientContext(symptoms="Explain my report.")

    async def slow_medbridge(*args, **kwargs):
        await asyncio.sleep(2)

    with patch("orchestrator.workflow.run_medbridge", slow_medbridge):
        with patch("orchestrator.workflow.WORKFLOW_TIMEOUT_SECONDS", 0.01):
            result = await run_medbridge_safe("x" * 40, patient)

    assert result.error is True
    assert "timed out" in result.error_message.lower()


def test_checkpoint_stores_clarification_round():
    patient = PatientContext(symptoms="ear pain")
    sid = save_session_checkpoint(
        report_text="Synthetic report text long enough.",
        patient=patient,
        trace=[{"agent": "Planner", "step": 1, "output": {}}],
        clarification_questions=["Any fever?"],
        clarification_round=MAX_CLARIFICATION_ROUNDS,
    )
    loaded = load_session_checkpoint(sid)
    assert loaded is not None
    assert loaded.clarification_round == MAX_CLARIFICATION_ROUNDS
