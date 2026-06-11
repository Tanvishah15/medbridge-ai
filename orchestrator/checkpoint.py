"""Session checkpointing for clarification loops and HandoffBuilder storage (Step 194)."""

import json
import logging
import uuid
from pathlib import Path

from pydantic import BaseModel, Field

from agents.models import PatientContext

logger = logging.getLogger(__name__)

CHECKPOINT_DIR = Path(__file__).resolve().parent.parent / ".medbridge_checkpoints"
HANDOFF_CHECKPOINT_DIR = CHECKPOINT_DIR / "handoff"
SESSION_DIR = CHECKPOINT_DIR / "sessions"


class SessionCheckpoint(BaseModel):
    session_id: str
    report_text: str
    patient: PatientContext
    trace: list[dict] = Field(default_factory=list)
    clarification_questions: list[str] = Field(default_factory=list)


def get_handoff_checkpoint_storage():
    from agent_framework import FileCheckpointStorage

    HANDOFF_CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    return FileCheckpointStorage(storage_path=str(HANDOFF_CHECKPOINT_DIR))


def _session_path(session_id: str) -> Path:
    return SESSION_DIR / f"{session_id}.json"


def save_session_checkpoint(
    report_text: str,
    patient: PatientContext,
    trace: list[dict],
    clarification_questions: list[str],
    session_id: str | None = None,
) -> str:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    sid = session_id or str(uuid.uuid4())
    checkpoint = SessionCheckpoint(
        session_id=sid,
        report_text=report_text,
        patient=patient,
        trace=trace,
        clarification_questions=clarification_questions,
    )
    _session_path(sid).write_text(checkpoint.model_dump_json(indent=2), encoding="utf-8")
    logger.info("Saved session checkpoint %s", sid)
    return sid


def load_session_checkpoint(session_id: str) -> SessionCheckpoint | None:
    path = _session_path(session_id)
    if not path.exists():
        return None
    return SessionCheckpoint.model_validate_json(path.read_text(encoding="utf-8"))


def delete_session_checkpoint(session_id: str) -> None:
    path = _session_path(session_id)
    if path.exists():
        path.unlink()
        logger.info("Deleted session checkpoint %s", session_id)
