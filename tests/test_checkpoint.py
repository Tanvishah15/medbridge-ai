from agents.models import PatientContext
from orchestrator.checkpoint import (
    delete_session_checkpoint,
    get_handoff_checkpoint_storage,
    load_session_checkpoint,
    save_session_checkpoint,
)
from orchestrator.trace import ReasoningTrace


def test_save_and_load_session_checkpoint():
    patient = PatientContext(symptoms="Ear pain", language="English")
    trace = [{"step": 1, "agent": "DocumentIntelligence", "output": "test"}]
    questions = ["Any fever?"]

    session_id = save_session_checkpoint(
        report_text="SYNTHETIC REPORT",
        patient=patient,
        trace=trace,
        clarification_questions=questions,
    )

    loaded = load_session_checkpoint(session_id)
    assert loaded is not None
    assert loaded.report_text == "SYNTHETIC REPORT"
    assert loaded.patient.symptoms == "Ear pain"
    assert loaded.clarification_questions == questions
    assert len(loaded.trace) == 1

    delete_session_checkpoint(session_id)
    assert load_session_checkpoint(session_id) is None


def test_reasoning_trace_from_list():
    steps = [
        {"step": 1, "agent": "Planner", "output": "plan"},
        {"step": 2, "agent": "DocumentIntelligence", "output": "parsed"},
    ]
    trace = ReasoningTrace.from_list(steps)
    assert len(trace.to_list()) == 2


def test_handoff_checkpoint_storage_created(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "orchestrator.checkpoint.HANDOFF_CHECKPOINT_DIR",
        tmp_path / "handoff",
    )
    storage = get_handoff_checkpoint_storage()
    assert storage is not None
    assert (tmp_path / "handoff").exists()
