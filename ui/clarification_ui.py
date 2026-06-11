"""Step 216 — clarification answer inputs for Streamlit UI."""

import ast

import streamlit as st


def format_question(question: str) -> str:
    text = str(question).strip()
    if text.startswith("{'question':") or text.startswith('{"question":'):
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, dict) and "question" in parsed:
                return str(parsed["question"])
        except (SyntaxError, ValueError):
            pass
    return text


def render_clarification_inputs(questions: list[str]) -> list[str]:
    """Show one text input per clarification question; return non-empty answers."""
    if not questions:
        return []

    st.divider()
    st.markdown("### ❓ Clarification needed")
    st.caption("Answer each question below, then click **Submit answers & explain**.")

    answers: list[str] = []
    for index, question in enumerate(questions):
        label = format_question(question)
        value = st.text_input(
            label,
            key=f"clarification_answer_{index}",
            placeholder="Type your answer here…",
        )
        if value.strip():
            answers.append(value.strip())

    if len(questions) > 1:
        st.info(f"Answered {len(answers)} of {len(questions)} questions.")

    return answers
