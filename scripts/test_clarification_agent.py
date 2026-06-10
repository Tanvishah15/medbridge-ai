import asyncio
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.clarification_agent import get_clarification_questions
from agents.document_agent import parse_report
from agents.models import PatientContext


async def main() -> None:
    report_path = ROOT / "data" / "synthetic_reports" / "rpt_ent_001.txt"
    report_text = report_path.read_text(encoding="utf-8")

    patient = PatientContext(
        symptoms="Mere kaan mein 3 din se ras aa rahi hai. Yeh report samjhao.",
        language="Hindi",
        literacy_level="simple",
        audience="patient",
    )

    print("=== Step 131 — Hindi ear discharge scenario ===")
    print(f"Report: {report_path.name}")
    print(f"Patient: {patient.symptoms}\n")

    report = await parse_report(report_text)
    questions = await get_clarification_questions(report, patient)

    print("=== Clarification Questions ===")
    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}")

    combined = " ".join(questions).lower()
    symptoms_lower = patient.symptoms.lower()
    checks = {
        "1-3 questions returned": 1 <= len(questions) <= 3,
        "asks about fever (bukhar/fever)": any(
            term in combined for term in ["bukhar", "fever", "बुखार"]
        ),
        "asks about pain (dard/pain)": any(
            term in combined for term in ["dard", "pain", "दर्द"]
        ),
        "duration covered (question or already in symptoms)": any(
            term in combined for term in ["din", "days", "duration", "कितने", "kitne"]
        )
        or any(term in symptoms_lower for term in ["din", "days"]),
    }

    print("\n=== Step 132 Checks ===")
    for label, passed in checks.items():
        print(f"  {label}: {'PASS' if passed else 'FAIL'}")

    if all(checks.values()):
        print("\nClarification agent test PASSED")
    else:
        print("\nClarification agent test PARTIAL — review output above")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
