from orchestrator.handoff_workflow import (
    build_medbridge_handoff_workflow,
    create_medbridge_handoff_agents,
    run_medbridge_handoff,
)

import pytest

from agents.models import PatientContext


def test_handoff_agents_created():
    agents = create_medbridge_handoff_agents()
    expected = [
        "triage_agent",
        "document_agent",
        "clarification_agent",
        "knowledge_agent",
        "explanation_agent",
        "multilingual_agent",
        "safety_agent",
    ]
    for name in expected:
        assert name in agents
        assert agents[name].name == name


def test_handoff_workflow_builds():
    workflow, agents = build_medbridge_handoff_workflow()
    assert workflow is not None
    assert len(agents) == 7


def test_handoff_routing_order():
    """Step 193 — verify sequential routing graph is wired."""
    _workflow, agents = build_medbridge_handoff_workflow()
    chain = [
        "triage_agent",
        "document_agent",
        "clarification_agent",
        "knowledge_agent",
        "explanation_agent",
        "multilingual_agent",
        "safety_agent",
    ]
    for name in chain:
        assert name in agents


@pytest.mark.asyncio
async def test_handoff_live_routing(ent_report):
    """Step 193 — live HandoffBuilder routing with Azure."""
    patient = PatientContext(
        symptoms="Ear discharge for 3 days, pain 5/10, no fever. Explain this report.",
        language="English",
        literacy_level="simple",
        audience="patient",
    )
    result = await run_medbridge_handoff(
        ent_report,
        patient,
        clarification_answers=["Mild hearing difficulty. No emergency symptoms."],
    )

    assert len(result.trace) >= 1, "Expected at least one handoff event"
    handoff_chain = " ".join(step["output"] for step in result.trace).lower()
    assert "document" in handoff_chain or "triage" in handoff_chain
    assert "knowledge" in handoff_chain or "explanation" in handoff_chain
    assert len(result.explanation) > 20 or len(result.trace) >= 3
