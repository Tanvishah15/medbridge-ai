"""Streamlit UI for MedBridge AI — Steps 212+ (Phase 7)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import asyncio
import ast

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agents.models import PatientContext
from orchestrator.workflow import run_medbridge_safe

DEMO_REPORTS = {
    "— Select demo report —": None,
    "ENT — Otitis Media (rpt_ent_001)": ROOT / "data" / "synthetic_reports" / "rpt_ent_001.txt",
    "Blood — Diabetes (rpt_blood_001)": ROOT / "data" / "synthetic_reports" / "rpt_blood_001.txt",
    "MRI — Brain (rpt_mri_001)": ROOT / "data" / "synthetic_reports" / "rpt_mri_001.txt",
}

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


def _load_demo_report(name: str) -> str:
    path = DEMO_REPORTS.get(name)
    if path and path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _format_question(question: str) -> str:
    text = str(question).strip()
    if text.startswith("{'question':") or text.startswith('{"question":'):
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, dict) and "question" in parsed:
                return str(parsed["question"])
        except (SyntaxError, ValueError):
            pass
    return text


def render_reasoning_trace(trace: list[dict]) -> None:
    """Step 189 — visible multi-step reasoning for judges."""
    st.markdown("### 🧠 How MedBridge agents reasoned")
    st.caption(
        "Sequential: Planner → Document → Clarify → Knowledge → Explain → "
        "Self-Reflection → Translate → Safety. "
        "Alternative: HandoffBuilder mesh in orchestrator/handoff_workflow.py"
    )

    if not trace:
        st.info("No trace available yet. Run the workflow to see agent steps.")
        return

    for step in trace:
        icon = AGENT_ICONS.get(step.get("agent", ""), "🤖")
        with st.expander(f"{icon} Step {step.get('step')} — {step.get('agent')}", expanded=True):
            st.write(step.get("output", ""))


def render_result(result) -> None:
    if result.error:
        st.error(result.error_message or "Something went wrong. Please try again.")
        return

    if result.clarification_needed:
        st.warning("I need a bit more information before explaining:")
        for question in result.clarification_questions:
            st.write(f"• {_format_question(question)}")
        if result.session_id:
            st.caption(f"Session checkpoint: `{result.session_id}`")
        return

    if result.safety_passed:
        st.success("✅ Safety validated")
    else:
        st.error("⚠️ Response adjusted for safety")

    st.markdown("### Your explanation")
    st.write(result.explanation)

    if result.citations:
        st.caption("Sources: " + ", ".join(result.citations))

    if result.safety_notes:
        st.caption("Safety notes: " + ", ".join(str(n) for n in result.safety_notes))


st.set_page_config(page_title="MedBridge AI", page_icon="🏥", layout="wide")

st.title("MedBridge AI")
st.caption("Don't just translate my medical report. Help me understand what's happening to me.")
st.warning(
    "Demo only · Synthetic data · Not medical advice · Always consult your doctor.",
    icon="⚠️",
)

st.sidebar.header("Settings")
language = st.sidebar.selectbox("Language", ["English", "Hindi", "Spanish", "Arabic"])
audience = st.sidebar.selectbox("Audience", ["patient", "family"])
literacy = st.sidebar.selectbox("Literacy Level", ["simple", "standard"])

demo_choice = st.sidebar.selectbox("Load demo report", list(DEMO_REPORTS.keys()))
if demo_choice != "— Select demo report —":
    st.session_state["demo_report_text"] = _load_demo_report(demo_choice)

default_report = st.session_state.get("demo_report_text", "")
report = st.text_area(
    "Paste your medical report (synthetic demo data only)",
    value=default_report,
    height=200,
)
symptoms = st.text_input("Describe your symptoms or question")
uploaded = st.file_uploader("Or upload a synthetic report (PDF or TXT)", type=["pdf", "txt"])

if "pending_clarification" not in st.session_state:
    st.session_state.pending_clarification = False
if "medbridge_session_id" not in st.session_state:
    st.session_state.medbridge_session_id = None
if "clarification_questions" not in st.session_state:
    st.session_state.clarification_questions = []
if "last_trace" not in st.session_state:
    st.session_state.last_trace = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

clarification_answers = ""
if st.session_state.pending_clarification:
    st.divider()
    st.markdown("### ❓ Clarification needed")
    st.caption("Answer below, then click **Understand My Report** again.")
    for question in st.session_state.clarification_questions:
        st.write(f"• {_format_question(question)}")
    clarification_answers = st.text_area(
        "Your answers (one per line)",
        height=120,
        key="clarification_answers_input",
        placeholder="Haan, halka bukhar hai.\nKaam mein dard hai.",
    )

col1, col2 = st.columns(2)
run_clicked = col1.button(
    "Submit answers & explain" if st.session_state.pending_clarification else "Understand My Report",
    type="primary",
)
clear_clicked = col2.button("Clear session")

if clear_clicked:
    st.session_state.pending_clarification = False
    st.session_state.medbridge_session_id = None
    st.session_state.clarification_questions = []
    st.session_state.last_trace = []
    st.session_state.last_result = None
    st.session_state.pop("demo_report_text", None)
    st.rerun()

if run_clicked:
    has_report = bool(report.strip()) or uploaded is not None
    if not has_report:
        st.error("Please paste or upload a synthetic demo report.")
    elif not symptoms.strip():
        st.error("Please describe your symptoms or question.")
    elif st.session_state.pending_clarification and not clarification_answers.strip():
        st.error("Please answer the clarification questions above (one answer per line).")
    else:
        answers_list = None
        if st.session_state.pending_clarification and clarification_answers.strip():
            answers_list = [line.strip() for line in clarification_answers.splitlines() if line.strip()]

        report_bytes = uploaded.getvalue() if uploaded is not None else None
        report_filename = uploaded.name if uploaded is not None else ""
        report_input = report if report.strip() else ""

        with st.spinner("MedBridge agents are reasoning..."):
            patient = PatientContext(
                symptoms=symptoms,
                language=language,
                literacy_level=literacy,
                audience=audience,
            )
            result = asyncio.run(
                run_medbridge_safe(
                    report_input,
                    patient,
                    clarification_answers=answers_list,
                    session_id=st.session_state.medbridge_session_id if answers_list else None,
                    report_bytes=report_bytes,
                    report_filename=report_filename,
                )
            )

        st.session_state.last_trace = result.trace
        st.session_state.pending_clarification = result.clarification_needed
        st.session_state.medbridge_session_id = result.session_id if result.clarification_needed else None
        st.session_state.clarification_questions = (
            result.clarification_questions if result.clarification_needed else []
        )
        if result.clarification_needed:
            st.session_state.last_result = None
            st.rerun()
        else:
            st.session_state.last_result = result

if st.session_state.last_result and not st.session_state.pending_clarification:
    st.divider()
    render_result(st.session_state.last_result)

if st.session_state.last_trace:
    st.divider()
    render_reasoning_trace(st.session_state.last_trace)
