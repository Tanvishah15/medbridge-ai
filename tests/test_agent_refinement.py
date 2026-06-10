import asyncio
import time

import pytest

from agents.clarification_agent import get_clarification_questions
from agents.document_agent import parse_report
from agents.explanation_agent import generate_explanation
from agents.knowledge_agent import retrieve_medical_knowledge
from agents.models import PatientContext, ReportStructure
from agents.multilingual_agent import translate_explanation
from agents.safety_agent import validate_response
from agents.utils import has_disclaimer, has_empathy_tone


# --- Steps 151-153: Document agent ---


@pytest.mark.asyncio
async def test_document_agent_parses_blood_report(blood_report):
    result = await parse_report(blood_report)
    combined = " ".join([result.diagnosis, *result.findings]).lower()
    assert "diabetes" in combined or "glucose" in combined or "hba1c" in combined


@pytest.mark.asyncio
async def test_document_agent_parses_mri_report(mri_report):
    result = await parse_report(mri_report)
    combined = " ".join([result.diagnosis, result.affected_area, *result.findings]).lower()
    assert "microvascular" in combined or "ischemic" in combined or "brain" in combined


@pytest.mark.asyncio
async def test_document_agent_handles_empty_input():
    result = await parse_report("")
    assert result.diagnosis == "No report provided"
    assert result.findings


@pytest.mark.asyncio
async def test_document_agent_handles_malformed_input():
    result = await parse_report("abc xyz ???")
    assert result.diagnosis
    assert "malformed" in result.findings[0].lower() or "short" in result.findings[0].lower()


# --- Steps 154-156: Knowledge agent ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "term",
    [
        "What is Otitis Media?",
        "Type 2 Diabetes",
        "Hypertension",
        "LDL Cholesterol",
        "Microvascular changes",
    ],
)
async def test_knowledge_agent_five_medical_terms(term):
    result = await retrieve_medical_knowledge(term)
    answer = result["answer"].lower()
    assert answer
    assert result["citations"] or "source" in answer or "【" in result["answer"]
    assert result["ungrounded_drugs"] == []


# --- Steps 157-160: Clarification agent ---


@pytest.mark.asyncio
async def test_clarification_agent_english(ent_report):
    report = ReportStructure(
        diagnosis="Otitis Media",
        findings=["Middle ear fluid present"],
        affected_area="Middle ear",
        raw_text=ent_report,
    )
    patient = PatientContext(
        symptoms="Fluid from my ear.",
        language="English",
    )
    questions = await get_clarification_questions(report, patient)
    assert len(questions) <= 3


@pytest.mark.asyncio
async def test_clarification_agent_hindi(ent_report):
    report = ReportStructure(
        diagnosis="Otitis Media",
        findings=["Middle ear fluid present"],
        raw_text=ent_report,
    )
    patient = PatientContext(
        symptoms="Mere kaan se ras aa raha hai.",
        language="Hindi",
    )
    questions = await get_clarification_questions(report, patient)
    assert len(questions) <= 3


@pytest.mark.asyncio
async def test_clarification_skips_when_symptoms_complete(ent_report):
    report = ReportStructure(
        diagnosis="Otitis Media",
        findings=["Middle ear fluid present"],
        raw_text=ent_report,
    )
    patient = PatientContext(
        symptoms="Ear pain 6/10 for 3 days, no fever, fluid leaking.",
        language="English",
    )
    questions = await get_clarification_questions(report, patient)
    assert questions == []


# --- Steps 161-163: Explanation agent ---


@pytest.mark.asyncio
async def test_explanation_low_literacy():
    explanation = await generate_explanation(
        report_summary='{"diagnosis": "Otitis Media"}',
        knowledge="Ear fluid can cause discharge.",
        symptoms="Fluid from ear for 3 days.",
        literacy_level="simple",
    )
    assert len(explanation.split(".")) >= 1
    assert has_empathy_tone(explanation)


@pytest.mark.asyncio
async def test_explanation_standard_literacy():
    explanation = await generate_explanation(
        report_summary='{"diagnosis": "Type 2 Diabetes"}',
        knowledge="Elevated glucose indicates diabetes management is needed.",
        symptoms="Feeling tired and thirsty.",
        literacy_level="standard",
    )
    assert len(explanation) > 80
    assert has_empathy_tone(explanation)


# --- Steps 164-166: Multilingual agent ---


@pytest.mark.asyncio
async def test_multilingual_spanish_grandmother():
    translated = await translate_explanation(
        explanation="Your report shows middle ear fluid. Follow your doctor's advice.",
        target_language="Spanish",
        audience="family",
    )
    assert has_disclaimer(translated)
    assert len(translated) > 20


@pytest.mark.asyncio
async def test_multilingual_arabic_family():
    translated = await translate_explanation(
        explanation="Your MRI shows mild chronic changes. Discuss with your neurologist.",
        target_language="Arabic",
        audience="family",
    )
    assert has_disclaimer(translated)
    assert len(translated) > 20


# --- Steps 167-170: Safety agent ---


@pytest.mark.asyncio
async def test_safety_blocks_diagnosis():
    result = await validate_response("You definitely have diabetes.")
    assert not result.get("safe", True)
    assert "doctor" in result["revised_response"].lower() or "healthcare" in result["revised_response"].lower()


@pytest.mark.asyncio
async def test_safety_blocks_prescription():
    result = await validate_response("Take ibuprofen 800mg three times daily and stop your current medication.")
    assert not result.get("safe", True)
    revised = result["revised_response"].lower()
    assert "ibuprofen" not in revised or "doctor" in revised


@pytest.mark.asyncio
async def test_safety_emergency_escalation():
    result = await validate_response("Patient reports chest pain and confusion.")
    revised = result["revised_response"].lower()
    assert "emergency" in revised or "immediately" in revised


@pytest.mark.asyncio
async def test_safety_safe_response_passes_through():
    safe_text = (
        "Your report shows findings to discuss with your doctor. "
        "This is educational information, not medical advice."
    )
    result = await validate_response(safe_text)
    assert result.get("safe") is True
    assert result.get("issues") == []
    assert safe_text in result["revised_response"]


# --- Step 173: Async end-to-end chain ---


@pytest.mark.asyncio
async def test_async_agent_chain(ent_report):
    report = await parse_report(ent_report)
    assert report.diagnosis

    questions = await get_clarification_questions(
        report,
        PatientContext(symptoms="Ear pain 5/10 for 2 days, no fever.", language="English"),
    )
    assert len(questions) <= 3

    knowledge = await retrieve_medical_knowledge(
        f"{report.diagnosis} ear discharge",
        report.model_dump_json(),
    )
    assert knowledge["answer"]

    explanation = await generate_explanation(
        report.model_dump_json(),
        knowledge["answer"],
        "Ear discharge for 3 days.",
        literacy_level="simple",
    )
    assert explanation

    safety = await validate_response(explanation)
    assert safety.get("revised_response")


# --- Step 171: Timeout constant ---


def test_agent_timeout_is_30_seconds():
    from agents.base import AGENT_TIMEOUT_SECONDS

    assert AGENT_TIMEOUT_SECONDS == 30
