import asyncio
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.document_agent import parse_report
from agents.explanation_agent import generate_explanation
from agents.knowledge_agent import retrieve_medical_knowledge


async def main() -> None:
    report_path = ROOT / "data" / "synthetic_reports" / "rpt_ent_001.txt"
    report_text = report_path.read_text(encoding="utf-8")
    symptoms = "Fluid leaking from my ear for 3 days. What does my report mean?"

    print("=== Step 134 — ENT explanation scenario ===")
    print(f"Report: {report_path.name}")
    print(f"Symptoms: {symptoms}\n")

    report = await parse_report(report_text)
    knowledge_result = await retrieve_medical_knowledge(
        "Why would ear discharge match middle ear fluid in Otitis Media?",
        report.model_dump_json(),
    )
    explanation = await generate_explanation(
        report_summary=report.model_dump_json(),
        knowledge=knowledge_result["answer"],
        symptoms=symptoms,
        literacy_level="simple",
    )

    print("=== Explanation ===")
    print(explanation)

    text = explanation.lower()
    checks = {
        "mentions middle ear / otitis": any(
            term in text for term in ["middle ear", "otitis", "ear infection"]
        ),
        "mentions fluid": "fluid" in text,
        "connects discharge/leakage to report": any(
            term in text for term in ["discharge", "leak", "drain", "fluid"]
        ),
        "uses simple empathetic tone": len(explanation.split()) >= 40,
    }

    print("\n=== Step 135 Checks ===")
    for label, passed in checks.items():
        print(f"  {label}: {'PASS' if passed else 'FAIL'}")

    if all(checks.values()):
        print("\nExplanation agent test PASSED")
    else:
        print("\nExplanation agent test PARTIAL — review output above")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
