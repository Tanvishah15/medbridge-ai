from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    return _pages_to_text(reader)


def extract_text_from_pdf_bytes(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    return _pages_to_text(reader)


def _pages_to_text(reader: PdfReader) -> str:
    parts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(part for part in parts if part).strip()


def resolve_report_text(
    report_text: str = "",
    report_bytes: bytes | None = None,
    filename: str = "",
) -> str:
    if report_bytes:
        name = (filename or "").lower()
        if name.endswith(".pdf"):
            extracted = extract_text_from_pdf_bytes(report_bytes)
            if not extracted.strip():
                raise ValueError("Could not extract text from the uploaded PDF.")
            return extracted
        return report_bytes.decode("utf-8", errors="replace").strip()

    if report_text.strip():
        path = Path(report_text)
        if path.exists() and path.suffix.lower() == ".pdf":
            extracted = extract_text_from_pdf(str(path))
            if not extracted.strip():
                raise ValueError(f"Could not extract text from PDF: {path}")
            return extracted
        return report_text.strip()

    raise ValueError("Please provide report text or upload a synthetic demo report file.")
