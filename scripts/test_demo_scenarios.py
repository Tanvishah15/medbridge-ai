"""Step 200 — CLI runner for all 3 hackathon demo scenarios."""

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

DATA = ROOT / "data" / "synthetic_reports"


async def demo_1_hindi_ent() -> bool:
    print("\n=== Demo 1: Hindi ENT + clarification loop ===")
    report = (DATA / "rpt_ent_001.txt").read_text(encoding="utf-8")
    patient = PatientContext(
        symptoms="Mere kaan mein 3 din se ras aa rahi hai. Yeh report samjhao.",
        language="Hindi",
        literacy_level="simple",
        audience="patient",
    )
    round1 = await run_medbridge(report, patient)
    print("Clarification needed:", round1.clarification_needed)
    print("Questions:", round1.clarification_questions)
    if not round1.clarification_needed:
        return False

    round2 = await run_medbridge(
        "",
        patient,
        clarification_answers=["Haan, halka bukhar hai. Kaan mein dard bhi hai."],
        session_id=round1.session_id,
    )
    print("Explanation preview:", round2.explanation[:280], "...")
    print("Safety passed:", round2.safety_passed)
    return round2.clarification_needed is False and len(round2.explanation) > 50


async def demo_2_spanish_blood() -> bool:
    print("\n=== Demo 2: Spanish grandmother / blood test ===")
    report = (DATA / "rpt_blood_001.txt").read_text(encoding="utf-8")
    patient = PatientContext(
        symptoms=(
            "Explain this blood test to my grandmother in Spanish. "
            "She is worried about the sugar numbers."
        ),
        language="Spanish",
        literacy_level="simple",
        audience="family",
    )
    result = await run_medbridge(
        report,
        patient,
        clarification_answers=[
            "No fever. Mild tiredness for 2 weeks.",
            "Pain level 2/10. No chest pain.",
        ],
    )
    print("Explanation preview:", result.explanation[:280], "...")
    print("Citations:", result.citations[:3] if result.citations else [])
    print("Safety passed:", result.safety_passed)
    return result.clarification_needed is False and len(result.explanation) > 50


async def demo_3_arabic_mri() -> bool:
    print("\n=== Demo 3: Arabic family / brain MRI ===")
    report = (DATA / "rpt_mri_001.txt").read_text(encoding="utf-8")
    patient = PatientContext(
        symptoms="لخص تقرير الرنين المغناطيسي لعائلتي",
        language="Arabic",
        literacy_level="simple",
        audience="family",
    )
    result = await run_medbridge(
        report,
        patient,
        clarification_answers=[
            "No new symptoms. Mild forgetfulness for months.",
            "No headache or vision changes.",
        ],
    )
    print("Explanation preview:", result.explanation[:280], "...")
    print("Safety passed:", result.safety_passed)
    return result.clarification_needed is False and len(result.explanation) > 50


async def main() -> None:
    results = {
        "Hindi ENT": await demo_1_hindi_ent(),
        "Spanish blood": await demo_2_spanish_blood(),
        "Arabic MRI": await demo_3_arabic_mri(),
    }
    print("\n=== Step 200 summary ===")
    for name, ok in results.items():
        print(f"{'PASS' if ok else 'FAIL'} — {name}")
    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
