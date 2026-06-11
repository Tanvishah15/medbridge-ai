"""Step 200 — End-to-end tests for all 3 hackathon demo scenarios.

See docs/demo_scenarios.md for persona details and judge talking points.
"""

import re

import pytest

from agents.models import PatientContext
from orchestrator.workflow import run_medbridge

ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


@pytest.mark.asyncio
async def test_demo_scenario_1_hindi_ent_clarification_loop(ent_report):
    """Demo 1 — Hindi patient, ENT report, two-round clarification loop."""
    patient = PatientContext(
        symptoms="Mere kaan mein 3 din se ras aa rahi hai. Yeh report samjhao.",
        language="Hindi",
        literacy_level="simple",
        audience="patient",
    )

    round1 = await run_medbridge(ent_report, patient)
    assert round1.clarification_needed is True
    assert 1 <= len(round1.clarification_questions) <= 3
    assert round1.session_id

    round2 = await run_medbridge(
        "",
        patient,
        clarification_answers=["Haan, halka bukhar hai. Kaan mein dard bhi hai."],
        session_id=round1.session_id,
    )
    assert round2.clarification_needed is False
    assert len(round2.explanation) > 50
    assert round2.safety_passed is True
    assert DEVANAGARI_RE.search(round2.explanation) or "kaan" in round2.explanation.lower()
    agents = [step["agent"] for step in round2.trace]
    assert "MedicalKnowledge" in agents
    assert "Multilingual" in agents
    assert "Safety" in agents


@pytest.mark.asyncio
async def test_demo_scenario_2_spanish_grandmother_blood(blood_report):
    """Demo 2 — Spanish family summary for grandmother worried about sugar numbers."""
    patient = PatientContext(
        symptoms=(
            "Explain this blood test to my grandmother in Spanish. "
            "She is worried about the sugar numbers."
        ),
        language="Spanish",
        literacy_level="simple",
        audience="family",
    )
    result = await run_medbridge(
        blood_report,
        patient,
        clarification_answers=[
            "No fever. Mild tiredness for 2 weeks.",
            "Pain level 2/10. No chest pain.",
        ],
    )

    assert result.clarification_needed is False
    assert len(result.explanation) > 50
    assert result.safety_passed is True
    text = result.explanation.lower()
    assert any(
        term in text
        for term in ["glucosa", "azúcar", "azucar", "diabetes", "colesterol", "médico", "medico"]
    )
    assert "you have diabetes" not in text
    assert result.citations or "doctor" in text or "médico" in text


@pytest.mark.asyncio
async def test_demo_scenario_3_arabic_family_mri(mri_report):
    """Demo 3 — Arabic family summary for brain MRI (microvascular changes)."""
    patient = PatientContext(
        symptoms="لخص تقرير الرنين المغناطيسي لعائلتي",
        language="Arabic",
        literacy_level="simple",
        audience="family",
    )
    result = await run_medbridge(
        mri_report,
        patient,
        clarification_answers=[
            "No new symptoms. Mild forgetfulness for months.",
            "No headache or vision changes.",
        ],
    )

    assert result.clarification_needed is False
    assert len(result.explanation) > 50
    assert result.safety_passed is True
    assert ARABIC_RE.search(result.explanation)
    text = result.explanation.lower()
    assert not any(
        phrase in text
        for phrase in ["take aspirin", "stop medication", "you have cancer"]
    )
    agents = [step["agent"] for step in result.trace]
    assert "MedicalKnowledge" in agents
    assert "Multilingual" in agents
    assert "Safety" in agents
