from ui.citation_format import (
    FOUNDRY_IQ_LABEL,
    format_citations_for_display,
    strip_citations_from_text,
)


def test_format_azure_chunk_citations():
    raw = ["【4:1†source】", "【4:4†source】", "【4:0†source】"]
    assert format_citations_for_display(raw) == [FOUNDRY_IQ_LABEL]


def test_format_named_source_citations():
    raw = ["【source: otitis_media.md】", "【source: symptom_connections.md】"]
    assert format_citations_for_display(raw) == ["Otitis Media", "Symptom Connections"]


def test_strip_inline_citations_and_sources_line():
    text = (
        "Your ear has fluid.【4:1†source】\n\n"
        "Sources: 【4:1†source】, 【4:4†source】"
    )
    cleaned = strip_citations_from_text(text)
    assert "【" not in cleaned
    assert "Sources:" not in cleaned
    assert "Your ear has fluid." in cleaned
