"""Generate synthetic PDF reports from TXT sources (Step 196-197 helper)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "data" / "synthetic_reports"


def _ascii_safe(text: str) -> str:
    return text.replace("\u2014", "-").replace("\u2013", "-")


def _write_pdf(text: str, output_path: Path) -> None:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    for line in _ascii_safe(text).splitlines():
        if not line.strip():
            pdf.ln(4)
            continue
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 6, line)
    pdf.output(str(output_path))


def main() -> None:
    for txt_path in REPORTS_DIR.glob("rpt_*.txt"):
        pdf_path = txt_path.with_suffix(".pdf")
        text = txt_path.read_text(encoding="utf-8")
        _write_pdf(text, pdf_path)
        print(f"Created {pdf_path.name}")


if __name__ == "__main__":
    main()
