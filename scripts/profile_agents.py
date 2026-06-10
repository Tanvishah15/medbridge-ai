"""Step 174 — Profile agent latency (slowest agent identification)."""

import asyncio
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.clarification_agent import get_clarification_questions
from agents.document_agent import parse_report
from agents.explanation_agent import generate_explanation
from agents.knowledge_agent import retrieve_medical_knowledge
from agents.models import PatientContext, ReportStructure
from agents.multilingual_agent import translate_explanation
from agents.safety_agent import validate_response


async def _timed(label: str, coro):
    start = time.perf_counter()
    result = await coro
    elapsed = time.perf_counter() - start
    return label, elapsed, result


async def main():
    ent_report = (ROOT / "data" / "synthetic_reports" / "rpt_ent_001.txt").read_text(encoding="utf-8")
    report = ReportStructure(
        diagnosis="Otitis Media",
        findings=["Middle ear fluid present"],
        raw_text=ent_report,
    )
    patient = PatientContext(
        symptoms="Ear discharge for 3 days, pain 5/10, no fever.",
        language="English",
    )

    tasks = [
        _timed("DocumentIntelligenceAgent", parse_report(ent_report)),
        _timed(
            "ClarificationAgent",
            get_clarification_questions(report, patient),
        ),
        _timed(
            "MedicalKnowledgeAgent",
            retrieve_medical_knowledge("What is Otitis Media?", report.model_dump_json()),
        ),
        _timed(
            "PatientExplanationAgent",
            generate_explanation(
                report.model_dump_json(),
                "Ear fluid can cause discharge.",
                patient.symptoms,
                literacy_level="simple",
            ),
        ),
        _timed(
            "MultilingualAgent",
            translate_explanation(
                "Your report shows middle ear fluid.",
                "Hindi",
                audience="patient",
            ),
        ),
        _timed(
            "SafetyAgent",
            validate_response("Educational info only. Consult your doctor."),
        ),
    ]

    results = await asyncio.gather(*tasks)
    results.sort(key=lambda item: item[1], reverse=True)

    print("\n=== MedBridge Agent Latency Profile (Step 174) ===\n")
    for label, elapsed, _ in results:
        print(f"{label:30s} {elapsed:6.2f}s")

    slowest = results[0]
    print(f"\nSlowest agent: {slowest[0]} ({slowest[1]:.2f}s)")
    print("\nTip (Step 175): Clarification + Multilingual use MODEL_DEPLOYMENT_FAST if set.")


if __name__ == "__main__":
    asyncio.run(main())
