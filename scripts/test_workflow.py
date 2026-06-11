"""CLI smoke test for MedBridge workflow (Step 183)."""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from agents.models import PatientContext
from orchestrator.workflow import run_medbridge


async def main():
    ent_report = (ROOT / "data" / "synthetic_reports" / "rpt_ent_001.txt").read_text(encoding="utf-8")
    patient = PatientContext(
        symptoms="Mere kaan mein 3 din se ras aa rahi hai. Yeh report samjhao.",
        language="Hindi",
        literacy_level="simple",
        audience="patient",
    )

    print("=== Run 1: clarification expected ===")
    result = await run_medbridge(ent_report, patient)
    print("clarification_needed:", result.clarification_needed)
    print("questions:", result.clarification_questions)

    if result.clarification_needed:
        print("\n=== Run 2: with clarification answers ===")
        result = await run_medbridge(
            ent_report,
            patient,
            clarification_answers=[
                "Haan, halka bukhar hai.",
                "Kaam mein dard hai.",
            ],
        )
        print("explanation preview:", result.explanation[:300], "...")
        print("citations:", result.citations)
        print("safety_passed:", result.safety_passed)


if __name__ == "__main__":
    asyncio.run(main())
