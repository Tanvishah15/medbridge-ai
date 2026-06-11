"""Step 217 — expandable reasoning trace panel for judges."""

import json

import streamlit as st

AGENT_ICONS = {
    "Planner": "🗺️",
    "SelfReflection": "🔍",
    "SelfReflectionRetry": "🔍",
    "MedicalKnowledgeRetry": "📚",
    "PatientExplanationRetry": "💬",
    "DocumentIntelligence": "📄",
    "Clarification": "❓",
    "MedicalKnowledge": "📚",
    "PatientExplanation": "💬",
    "Multilingual": "🌐",
    "Safety": "🛡️",
    "Error": "⚠️",
}

TRACE_CAPTION = (
    "Sequential: Planner → Document → Clarify → Knowledge → Explain → "
    "Self-Reflection → Translate → Safety. "
    "Alternative: HandoffBuilder mesh in orchestrator/handoff_workflow.py"
)


def agent_icon(agent_name: str) -> str:
    return AGENT_ICONS.get(agent_name, "🤖")


def format_step_output(output) -> str:
    if output is None:
        return ""
    if isinstance(output, (dict, list)):
        return json.dumps(output, ensure_ascii=False, indent=2)
    return str(output)


def render_reasoning_trace(trace: list[dict]) -> None:
    """Playbook Step 217 — outer expander with per-agent step details."""
    with st.expander("🧠 See how agents reasoned", expanded=False):
        st.caption(TRACE_CAPTION)

        if not trace:
            st.info("No trace available yet. Run the workflow to see agent steps.")
            return

        st.caption(f"{len(trace)} agent steps recorded")

        for index, step in enumerate(trace):
            agent = step.get("agent", "Unknown")
            icon = agent_icon(agent)
            step_num = step.get("step", index + 1)
            expanded = index == len(trace) - 1
            with st.expander(f"{icon} Step {step_num} — {agent}", expanded=expanded):
                st.code(format_step_output(step.get("output", "")), language="json")
