"""Format Foundry IQ / knowledge-base citations for Streamlit display."""

import re

_NAMED_SOURCE = re.compile(r"【source:\s*([^】]+)】", re.I)
_AZURE_CHUNK = re.compile(r"【\d+:\d+†source】", re.I)
_ANY_BRACKET = re.compile(r"【[^】]+】")
_SOURCES_LINE = re.compile(r"^\s*Sources?:.*$", re.I | re.M)

FOUNDRY_IQ_LABEL = "MedBridge medical knowledge base (Foundry IQ)"


def _friendly_doc_name(name: str) -> str:
    base = name.strip()
    if base.lower().endswith(".md"):
        base = base[:-3]
    return base.replace("_", " ").replace("-", " ").strip().title()


def format_citations_for_display(citations: list[str]) -> list[str]:
    """Turn raw citation markers into short, human-readable source labels."""
    labels: list[str] = []
    has_azure_chunks = False

    for raw in citations:
        text = str(raw).strip()
        if not text:
            continue

        named = _NAMED_SOURCE.search(text)
        if named:
            label = _friendly_doc_name(named.group(1))
            if label not in labels:
                labels.append(label)
            continue

        if _AZURE_CHUNK.search(text) or "†source" in text.lower():
            has_azure_chunks = True
            continue

        if text.startswith("【") and text.endswith("】"):
            has_azure_chunks = True
            continue

        if text not in labels:
            labels.append(text)

    if has_azure_chunks and FOUNDRY_IQ_LABEL not in labels:
        labels.append(FOUNDRY_IQ_LABEL)

    return labels


def strip_citations_from_text(text: str) -> str:
    """Remove inline citation markers and trailing Sources lines from explanation text."""
    if not text:
        return text

    cleaned = _ANY_BRACKET.sub("", text)
    cleaned = _SOURCES_LINE.sub("", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()
