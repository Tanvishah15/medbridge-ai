import pytest

from agents.models import PatientContext
from orchestrator.workflow import run_medbridge


@pytest.mark.asyncio
async def test_workflow_ent_returns_clarification_first(ent_report):
    """Step 184 — ENT scenario without clarification answers."""
    patient = PatientContext(
        symptoms="Mere kaan mein 3 din se ras aa rahi hai. Yeh report samjhao.",
        language="Hindi",
        literacy_level="simple",
        audience="patient",
    )
    result = await run_medbridge(ent_report, patient)

    assert result.clarification_needed is True
    assert 1 <= len(result.clarification_questions) <= 3
    assert result.explanation == ""
    assert len(result.trace) >= 2
    assert result.trace[0]["agent"] == "DocumentIntelligence"
    assert result.trace[1]["agent"] == "Planner"
    assert result.trace[2]["agent"] == "Clarification"


@pytest.mark.asyncio
async def test_workflow_ent_hindi_full_explanation(ent_report):
    """Step 185 — ENT scenario with clarification answers → Hindi explanation."""
    patient = PatientContext(
        symptoms="Mere kaan mein 3 din se ras aa rahi hai. Yeh report samjhao.",
        language="Hindi",
        literacy_level="simple",
        audience="patient",
    )
    result = await run_medbridge(
        ent_report,
        patient,
        clarification_answers=[
            "Haan, halka bukhar hai.",
            "Kaam mein dard hai.",
        ],
    )

    assert result.clarification_needed is False
    assert len(result.explanation) > 50
    assert result.citations or "doctor" in result.explanation.lower()
    assert any("\u0900" <= ch <= "\u097f" for ch in result.explanation) or "kaan" in result.explanation.lower()
    assert result.safety_passed is True
    assert len(result.trace) >= 5
    agents = [step["agent"] for step in result.trace]
    assert agents[0] == "DocumentIntelligence"
    assert "Planner" in agents
    assert "MedicalKnowledge" in agents
    assert "Multilingual" in agents
    assert "Safety" in agents


@pytest.mark.asyncio
async def test_workflow_spanish_family_blood_report(blood_report):
    """Step 186 — Spanish grandmother / family blood test scenario."""
    patient = PatientContext(
        symptoms="Explain this blood test to my grandmother in Spanish. She is worried about the sugar numbers.",
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
    text = result.explanation.lower()
    assert any(
        term in text
        for term in ["glucosa", "azúcar", "diabetes", "colesterol", "doctor", "médico", "información"]
    )
    assert "you have diabetes" not in text
    assert result.safety_passed is True


@pytest.mark.asyncio
async def test_workflow_diabetes_blood_report(blood_report):
    """Step 187 — Diabetes blood report end-to-end."""
    patient = PatientContext(
        symptoms="My fasting glucose and HbA1c are high. What does this blood report mean?",
        language="English",
        literacy_level="standard",
        audience="patient",
    )
    result = await run_medbridge(
        blood_report,
        patient,
        clarification_answers=[
            "No fever. Thirst and tiredness for 3 weeks.",
            "Pain 1/10. No emergency symptoms.",
        ],
    )

    assert result.clarification_needed is False
    text = result.explanation.lower()
    assert any(term in text for term in ["glucose", "hba1c", "diabetes", "sugar", "cholesterol"])
    assert result.citations or "doctor" in text or "healthcare" in text
    assert result.safety_passed is True
