"""Step 218 — safety status indicator for Streamlit results."""

import streamlit as st


def safety_status_label(safety_passed: bool) -> str:
    if safety_passed:
        return "Safety validated"
    return "Response adjusted for safety"


def safety_status_icon(safety_passed: bool) -> str:
    return "✅" if safety_passed else "⚠️"


def render_safety_indicator(safety_passed: bool, safety_notes: list[str] | None = None) -> None:
    """Show green or red safety badge for judges."""
    label = safety_status_label(safety_passed)
    icon = safety_status_icon(safety_passed)
    css_class = "medbridge-safety-pass" if safety_passed else "medbridge-safety-fail"

    st.markdown(
        f"""
        <style>
        .medbridge-safety-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.55rem 0.9rem;
            border-radius: 999px;
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 0.75rem;
        }}
        .medbridge-safety-pass {{
            background: #ecfdf5;
            color: #047857;
            border: 1px solid #6ee7b7;
        }}
        .medbridge-safety-fail {{
            background: #fef2f2;
            color: #b91c1c;
            border: 1px solid #fca5a5;
        }}
        </style>
        <div class="medbridge-safety-badge {css_class}">
            <span>{icon}</span>
            <span>{label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    notes = [str(note).strip() for note in (safety_notes or []) if str(note).strip()]
    if notes:
        st.caption("Safety notes: " + " · ".join(notes))
