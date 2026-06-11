from pydantic import BaseModel, Field
from typing import Optional


class ReportStructure(BaseModel):
    diagnosis: str = ""
    findings: list[str] = Field(default_factory=list)
    affected_area: str = ""
    recommendations: list[str] = Field(default_factory=list)
    raw_text: str = ""


class PatientContext(BaseModel):
    symptoms: str = ""
    language: str = "English"
    literacy_level: str = "simple"  # simple | standard
    audience: str = "patient"       # patient | family


class ClarificationQuestion(BaseModel):
    question: str
    reason: str


class MedBridgeResponse(BaseModel):
    explanation: str
    citations: list[str] = Field(default_factory=list)
    clarification_needed: bool = False
    clarification_questions: list[str] = Field(default_factory=list)
    safety_passed: bool = True
    safety_notes: list[str] = Field(default_factory=list)
    trace: list[dict] = Field(default_factory=list)
    session_id: str | None = None
