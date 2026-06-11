from pathlib import Path

import pytest

from orchestrator.pdf_utils import extract_text_from_pdf, extract_text_from_pdf_bytes, resolve_report_text

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "synthetic_reports"


def _make_pdf(text: str, path: Path) -> None:
    from fpdf import FPDF

    safe_text = text.replace("\u2014", "-").replace("\u2013", "-")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    for line in safe_text.splitlines():
        if not line.strip():
            pdf.ln(4)
            continue
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 6, line)
    pdf.output(str(path))


@pytest.fixture
def synthetic_ent_pdf(tmp_path, ent_report):
    pdf_path = tmp_path / "rpt_ent_001.pdf"
    _make_pdf(ent_report, pdf_path)
    return pdf_path


def test_extract_text_from_synthetic_pdf(synthetic_ent_pdf):
    text = extract_text_from_pdf(str(synthetic_ent_pdf))
    assert "SYNTHETIC" in text
    assert "Otitis Media" in text or "otitis" in text.lower()


def test_extract_text_from_pdf_bytes(synthetic_ent_pdf):
    data = synthetic_ent_pdf.read_bytes()
    text = extract_text_from_pdf_bytes(data)
    assert "SYNTHETIC" in text


def test_resolve_report_text_from_uploaded_pdf(synthetic_ent_pdf):
    text = resolve_report_text(
        report_bytes=synthetic_ent_pdf.read_bytes(),
        filename="rpt_ent_001.pdf",
    )
    assert "middle ear" in text.lower() or "otitis" in text.lower()


def test_resolve_report_text_from_txt_bytes(ent_report):
    text = resolve_report_text(
        report_bytes=ent_report.encode("utf-8"),
        filename="rpt_ent_001.txt",
    )
    assert "Otitis Media" in text
