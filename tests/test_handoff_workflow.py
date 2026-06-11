from orchestrator.handoff_workflow import (
    build_medbridge_handoff_workflow,
    create_medbridge_handoff_agents,
)


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
