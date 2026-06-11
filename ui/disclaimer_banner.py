"""Step 220 — prominent demo disclaimer banner at top of Streamlit UI."""

import streamlit as st

DISCLAIMER_BANNER_TEXT = (
    "Demo only. Synthetic data. Not medical advice. Always consult your doctor."
)


def render_disclaimer_banner() -> None:
    """Show a fixed-style warning banner for judges and hackathon compliance."""
    st.markdown(
        f"""
        <style>
        .medbridge-disclaimer-banner {{
            background: #fffbeb;
            color: #92400e;
            border: 1px solid #fcd34d;
            border-left: 5px solid #f59e0b;
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
            font-size: 0.95rem;
            font-weight: 600;
            line-height: 1.45;
            display: flex;
            align-items: center;
            gap: 0.55rem;
            box-shadow: 0 1px 2px rgba(146, 64, 14, 0.08);
        }}
        .medbridge-disclaimer-icon {{
            font-size: 1.1rem;
            flex-shrink: 0;
        }}
        </style>
        <div class="medbridge-disclaimer-banner" role="alert">
            <span class="medbridge-disclaimer-icon" aria-hidden="true">⚠️</span>
            <span>{DISCLAIMER_BANNER_TEXT}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
