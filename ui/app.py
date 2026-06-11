"""Streamlit UI for MedBridge AI — includes reasoning trace for judges (Step 189)."""

import asyncio
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agents.models import PatientContext
from orchestrator.workflow import run_medbridge

ROOT = Path(__file__).resolve().parent.parent
DEMO_REPORTS = {
    "— Select demo report —": None,
    "ENT — Otitis Media (rpt_ent_001)": ROOT / "data" / "synthetic_reports" / "rpt_ent_001.txt",
    "Blood — Diabetes (rpt_blood_001)": ROOT / "data" / "synthetic_reports" / "rpt_blood_001.txt",
    "MRI — Brain (rpt_mri_001)": ROOT / "data" / "synthetic_reports" / "rpt_mri_001.txt",
}

AGENT_ICONS = {
    "DocumentIntelligence": "📄",
    "Clarification": "❓",
    "MedicalKnowledge": "📚",
    "PatientExplanation": "💬",
    "Multilingual": "🌐",
    "Safety": "🛡️",
}


def _load_demo_report(name: str) -> str:
    path = DEMO_REPORTS.get(name)
    if path and path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def render_reasoning_trace(trace: list[dict]) -> None:
    """Step 189 — visible multi-step reasoning for judges."""
    st.markdown("### 🧠 How MedBridge agents reasoned")
    st.caption("Sequential pipeline: Document → Clarify → Knowledge → Explain → Translate → Safety")

    if not trace:
        st.info("No trace available yet. Run the workflow to see agent steps.")
        return

    for step in trace:
        icon = AGENT_ICONS.get(step.get("agent", ""), "🤖")
        with st.expander(f"{icon} Step {step.get('step')} — {step.get('agent')}", expanded=True):
            st.write(step.get("output", ""))


def render_result(result) -> None:
    if result.clarification_needed:
        st.warning("I need a bit more information before explaining:")
        for question in result.clarification_questions:
            st.write(f"• {question}")
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

if "pending_clarification" not in st.session_state:
    st.session_state.pending_clarification = False
if "last_trace" not in st.session_state:
    st.session_state.last_trace = []

clarification_answers = None
if st.session_state.pending_clarification:
    st.markdown("#### Clarification answers")
    clarification_answers = st.text_area(
        "Answer the questions above (one per line)",
        height=100,
        key="clarification_answers_input",
    )

col1, col2 = st.columns(2)
run_clicked = col1.button("Understand My Report", type="primary")
clear_clicked = col2.button("Clear session")

if clear_clicked:
    st.session_state.pending_clarification = False
    st.session_state.last_trace = []
    st.session_state.pop("demo_report_text", None)
    st.rerun()

if run_clicked:
    if not report.strip():
        st.error("Please paste a synthetic demo report.")
    elif not symptoms.strip():
        st.error("Please describe your symptoms or question.")
    else:
        answers_list = None
        if st.session_state.pending_clarification and clarification_answers:
            answers_list = [line.strip() for line in clarification_answers.splitlines() if line.strip()]

        with st.spinner("MedBridge agents are reasoning..."):
            patient = PatientContext(
                symptoms=symptoms,
                language=language,
                literacy_level=literacy,
                audience=audience,
            )
            result = asyncio.run(run_medbridge(report, patient, clarification_answers=answers_list))

        st.session_state.last_trace = result.trace
        st.session_state.pending_clarification = result.clarification_needed

        render_result(result)

if st.session_state.last_trace:
    st.divider()
    render_reasoning_trace(st.session_state.last_trace)
