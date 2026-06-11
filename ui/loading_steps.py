"""Step 223 — loading step indicators for Streamlit workflow runs."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import streamlit as st

ProgressCallback = Callable[[str], None]

LOADING_STEPS: list[dict[str, str]] = [
    {"key": "reading_report", "label": "Reading report"},
    {"key": "checking_symptoms", "label": "Checking symptoms"},
    {"key": "retrieving_knowledge", "label": "Retrieving knowledge"},
    {"key": "explaining", "label": "Explaining"},
    {"key": "validating_safety", "label": "Validating safety"},
]

STEP_INDEX = {step["key"]: index for index, step in enumerate(LOADING_STEPS)}


def format_step_chain(active_index: int) -> str:
    """Render playbook-style arrow chain with current step highlighted."""
    parts: list[str] = []
    for index, step in enumerate(LOADING_STEPS):
        label = step["label"]
        if index < active_index:
            parts.append(f"✅ {label}")
        elif index == active_index:
            parts.append(f"**{label}...**")
        else:
            parts.append(label)
    return " → ".join(parts)


def notify_progress(callback: ProgressCallback | None, step_key: str) -> None:
    if callback is not None:
        callback(step_key)


class LoadingStepTracker:
    """Update st.status + timeline as workflow phases complete."""

    def __init__(self, status: Any, timeline_placeholder: Any) -> None:
        self.status = status
        self.timeline = timeline_placeholder
        self(LOADING_STEPS[0]["key"])

    def __call__(self, step_key: str) -> None:
        index = STEP_INDEX.get(step_key, 0)
        step = LOADING_STEPS[index]
        self.status.update(label=f"{step['label']}...")
        self.timeline.markdown(format_step_chain(index))
