"""Streamlit UI for MedBridge AI — Steps 212+ (Phase 7)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import asyncio

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agents.models import PatientContext
from agents.utils import is_vague_symptom_message
from orchestrator.workflow import run_medbridge_safe
from ui.clarification_ui import format_question, render_clarification_inputs
from ui.demo_presets import SELECT_PLACEHOLDER, get_demo_preset, list_demo_labels, load_demo_report_text
from ui.grandmother_mode import apply_grandmother_mode
from ui.citation_format import format_citations_for_display, strip_citations_from_text
from ui.safety_indicator import render_safety_indicator
from ui.trace_panel import render_reasoning_trace


def _apply_demo_preset(label: str) -> None:
    """Step 215 — pre-load report, symptoms, and settings for a demo."""
    preset = get_demo_preset(label)
    if preset is None:
        return
    st.session_state.demo_report_text = load_demo_report_text(label)
    st.session_state.demo_symptoms = preset.symptoms
    st.session_state.ui_language = preset.language
    st.session_state.ui_audience = preset.audience
    st.session_state.ui_literacy = preset.literacy_level


def apply_medbridge_branding() -> None:
    """Step 214 — clean medical blue styling."""
    st.markdown(
        """
        <style>
        .medbridge-hero {
            background: #ffffff;
            padding: 1.5rem 1.75rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            border: 1px solid #e2e8f0;
            border-left: 5px solid #2563eb;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
        }
        .medbridge-hero h1 {
            color: #0f172a !important;
            font-size: 1.85rem !important;
            font-weight: 700 !important;
            margin: 0 !important;
            padding: 0 !important;
            letter-spacing: -0.02em;
        }
        .medbridge-hero p {
            color: #475569;
            margin: 0.4rem 0 0.75rem 0;
            font-size: 1rem;
            line-height: 1.5;
        }
        .medbridge-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }
        .medbridge-badge {
            display: inline-block;
            background: #eff6ff;
            color: #1d4ed8;
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 500;
            border: 1px solid #bfdbfe;
        }
        div[data-testid="stSidebar"] {
            background-color: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }
        div[data-testid="stSidebar"] h2 {
            color: #1e293b;
            font-size: 1.1rem;
        }
        div[data-testid="stSidebar"] label {
            color: #334155;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="medbridge-hero">
            <h1>🏥 MedBridge AI</h1>
            <p>Don't just translate my medical report. Help me understand what's happening to me.</p>
            <div class="medbridge-badges">
                <span class="medbridge-badge">6 reasoning agents</span>
                <span class="medbridge-badge">Foundry IQ</span>
                <span class="medbridge-badge">Synthetic demo</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result(result) -> None:
    if result.error:
        st.error(result.error_message or "Something went wrong. Please try again.")
        return

    if result.clarification_needed:
        st.warning("I need a bit more information before explaining:")
        for question in result.clarification_questions:
            st.write(f"• {format_question(question)}")
        if result.session_id:
            st.caption(f"Session checkpoint: `{result.session_id}`")
        return

    render_safety_indicator(result.safety_passed, result.safety_notes)

    st.markdown("### 💬 Your explanation")
    st.write(strip_citations_from_text(result.explanation))

    formatted_sources = format_citations_for_display(result.citations)
    if formatted_sources:
        st.caption("Sources: " + " · ".join(formatted_sources))


st.set_page_config(page_title="MedBridge AI", page_icon="🏥", layout="wide")

apply_medbridge_branding()
render_header()
st.warning(
    "Demo only · Synthetic data · Not medical advice · Always consult your doctor.",
    icon="⚠️",
)

st.sidebar.header("Settings")

if "ui_language" not in st.session_state:
    st.session_state.ui_language = "English"
if "ui_audience" not in st.session_state:
    st.session_state.ui_audience = "patient"
if "ui_literacy" not in st.session_state:
    st.session_state.ui_literacy = "simple"
if "demo_symptoms" not in st.session_state:
    st.session_state.demo_symptoms = ""

demo_choice = st.sidebar.selectbox("Load demo report", list_demo_labels(), key="demo_choice")
if demo_choice != SELECT_PLACEHOLDER:
    if st.session_state.get("_loaded_demo") != demo_choice:
        _apply_demo_preset(demo_choice)
        st.session_state._loaded_demo = demo_choice
        st.rerun()
    preset = get_demo_preset(demo_choice)
    if preset:
        st.sidebar.caption(preset.description)

language = st.sidebar.selectbox(
    "Language",
    ["English", "Hindi", "Spanish", "Arabic"],
    key="ui_language",
)
audience = st.sidebar.selectbox(
    "Audience",
    ["patient", "family"],
    key="ui_audience",
)
literacy = st.sidebar.selectbox(
    "Literacy Level",
    ["simple", "standard"],
    key="ui_literacy",
)

st.sidebar.divider()
if st.sidebar.button("👵 Explain to my grandmother", use_container_width=True, type="secondary"):
    mode = apply_grandmother_mode(st.session_state.get("demo_symptoms", ""))
    st.session_state.ui_audience = mode["audience"]
    st.session_state.ui_literacy = mode["literacy_level"]
    st.session_state.demo_symptoms = mode["symptoms"]
    st.rerun()
st.sidebar.caption(
    "Family mode: warm, simple tone for explaining to an elderly relative."
)

default_report = st.session_state.get("demo_report_text", "")
report = st.text_area(
    "Paste your medical report (synthetic demo data only)",
    value=default_report,
    height=200,
)
symptoms = st.text_input(
    "Describe your symptoms or question",
    value=st.session_state.get("demo_symptoms", ""),
    key="symptoms_input",
)
if symptoms.strip() and is_vague_symptom_message(symptoms):
    st.caption(
        "Tip: Add body-specific details (e.g. ear pain, discharge, fever) "
        "or reload the demo preset for best results."
    )
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

clarification_answers_list: list[str] = []
if st.session_state.pending_clarification:
    clarification_answers_list = render_clarification_inputs(
        st.session_state.clarification_questions
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
    for key in list(st.session_state.keys()):
        if str(key).startswith("clarification_answer_"):
            del st.session_state[key]
    st.session_state.last_trace = []
    st.session_state.last_result = None
    st.session_state.pop("demo_report_text", None)
    st.session_state.pop("demo_symptoms", None)
    st.session_state.pop("_loaded_demo", None)
    st.session_state.ui_language = "English"
    st.session_state.ui_audience = "patient"
    st.session_state.ui_literacy = "simple"
    st.rerun()

if run_clicked:
    has_report = bool(report.strip()) or uploaded is not None
    if not has_report:
        st.error("Please paste or upload a synthetic demo report.")
    elif not symptoms.strip():
        st.error("Please describe your symptoms or question.")
    elif st.session_state.pending_clarification and not clarification_answers_list:
        st.error("Please answer at least one clarification question above.")
    else:
        answers_list = None
        if st.session_state.pending_clarification and clarification_answers_list:
            answers_list = clarification_answers_list

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
            st.rerun()

if st.session_state.last_result and not st.session_state.pending_clarification:
    st.divider()
    render_result(st.session_state.last_result)

if st.session_state.last_trace:
    st.divider()
    render_reasoning_trace(st.session_state.last_trace)
