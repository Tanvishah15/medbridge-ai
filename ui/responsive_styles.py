"""Step 222 — mobile-friendly responsive styles for Streamlit UI."""

import streamlit as st

MOBILE_BREAKPOINT_PX = 768
NARROW_BREAKPOINT_PX = 480

RESPONSIVE_CSS = f"""
@media (max-width: {MOBILE_BREAKPOINT_PX}px) {{
    .medbridge-hero {{
        padding: 1rem 1.1rem !important;
        margin-bottom: 0.75rem !important;
    }}
    .medbridge-hero h1 {{
        font-size: 1.35rem !important;
        line-height: 1.25 !important;
    }}
    .medbridge-hero p {{
        font-size: 0.92rem !important;
    }}
    .medbridge-badges {{
        gap: 0.35rem !important;
    }}
    .medbridge-badge {{
        font-size: 0.72rem !important;
    }}
    .medbridge-disclaimer-banner {{
        font-size: 0.85rem !important;
        padding: 0.65rem 0.85rem !important;
        align-items: flex-start !important;
    }}
    .medbridge-safety-badge {{
        width: 100%;
        box-sizing: border-box;
        font-size: 0.88rem !important;
    }}
    div[data-testid="stMainBlockContainer"] {{
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }}
    div[data-testid="stMainBlockContainer"] h3 {{
        font-size: 1.05rem !important;
    }}
    div[data-testid="column"] {{
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }}
    div[data-testid="stHorizontalBlock"] {{
        flex-wrap: wrap !important;
        gap: 0.5rem !important;
    }}
    div[data-testid="stButton"] button {{
        width: 100% !important;
    }}
    div[data-testid="stTextArea"] textarea {{
        min-height: 140px !important;
    }}
    div[data-testid="stExpander"] pre {{
        white-space: pre-wrap !important;
        word-break: break-word !important;
        font-size: 0.78rem !important;
    }}
    section[data-testid="stSidebar"] {{
        min-width: 17rem !important;
    }}
}}

@media (max-width: {NARROW_BREAKPOINT_PX}px) {{
    .medbridge-hero h1 {{
        font-size: 1.15rem !important;
    }}
    .medbridge-disclaimer-banner {{
        font-size: 0.8rem !important;
    }}
}}
"""


def apply_responsive_styles() -> None:
    """Inject CSS so layout stacks cleanly on phone-width screens."""
    st.markdown(f"<style>{RESPONSIVE_CSS}</style>", unsafe_allow_html=True)
