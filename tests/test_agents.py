import pytest
from dotenv import load_dotenv
from pathlib import Path

from agents.clarification_agent import get_clarification_questions
from agents.document_agent import parse_report
from agents.explanation_agent import generate_explanation
from agents.knowledge_agent import retrieve_medical_knowledge
from agents.models import PatientContext, ReportStructure
from agents.multilingual_agent import translate_explanation
from agents.safety_agent import validate_response

load_dotenv()

ENT_REPORT = (Path(__file__).resolve().parent.parent / "data" / "synthetic_reports" / "rpt_ent_001.txt").read_text(
    encoding="utf-8"
)


@pytest.mark.asyncio
async def test_document_agent_parses_ent_report():
    result = await parse_report(ENT_REPORT)
    assert isinstance(result, ReportStructure)
    combined = " ".join([result.diagnosis, result.affected_area, *result.findings]).lower()
    assert "otitis media" in combined
    assert "fluid" in combined


@pytest.mark.asyncio
async def test_knowledge_agent_otitis_media():
    result = await retrieve_medical_knowledge("What is Otitis Media?")
    answer = result["answer"].lower()
    assert "otitis" in answer or "middle ear" in answer
    assert result["citations"] or "source" in answer or "†" in result["answer"]


@pytest.mark.asyncio
async def test_knowledge_agent_symptom_connection():
    result = await retrieve_medical_knowledge(
        "Why would ear discharge match a report showing middle ear fluid?"
    )
    answer = result["answer"].lower()
    assert "discharge" in answer or "drain" in answer
    assert "fluid" in answer


@pytest.mark.asyncio
async def test_clarification_agent_hindi_questions():
    report = ReportStructure(
        diagnosis="Otitis Media",
        findings=["Middle ear fluid present"],
        affected_area="Middle ear",
        recommendations=["Follow up in 7 days"],
        raw_text=ENT_REPORT,
    )
    patient = PatientContext(
        symptoms="Mere kaan mein 3 din se ras aa rahi hai. Yeh report samjhao.",
        language="Hindi",
    )
    questions = await get_clarification_questions(report, patient)
    assert 1 <= len(questions) <= 3
    combined = " ".join(questions).lower()
    assert "bukhar" in combined or "fever" in combined
    assert "dard" in combined or "pain" in combined


@pytest.mark.asyncio
async def test_explanation_agent_connects_symptoms():
    explanation = await generate_explanation(
        report_summary='{"diagnosis": "Otitis Media", "findings": ["Middle ear fluid present"]}',
        knowledge="Ear discharge can match middle ear fluid from infection.",
        symptoms="Fluid leaking from my ear for 3 days.",
        literacy_level="simple",
    )
    text = explanation.lower()
    assert "fluid" in text
    assert any(term in text for term in ["ear", "middle", "discharge", "leak"])


@pytest.mark.asyncio
async def test_multilingual_agent_hindi():
    translated = await translate_explanation(
        explanation="Your report shows middle ear fluid. Follow your doctor's advice.",
        target_language="Hindi",
        audience="patient",
    )
    assert any("\u0900" <= ch <= "\u097f" for ch in translated) or "doctor" in translated.lower()


@pytest.mark.asyncio
async def test_safety_agent_blocks_diagnosis():
    result = await validate_response(
        "You definitely have diabetes. Please stop taking your current medication."
    )
    revised = result.get("revised_response", "").lower()
    assert "you have diabetes" not in revised and "you definitely have" not in revised
    assert "doctor" in revised or "healthcare" in revised or "consult" in revised
    assert result.get("issues") or not result.get("safe", True)


@pytest.mark.asyncio
async def test_safety_agent_emergency_detection():
    result = await validate_response(
        "You may have an ear infection. The patient reports chest pain and confusion."
    )
    revised = result.get("revised_response", "").lower()
    assert "emergency" in revised or "immediately" in revised
