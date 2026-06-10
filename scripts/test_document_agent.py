import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.document_agent import parse_report


async def main() -> None:
    report_path = ROOT / "data" / "synthetic_reports" / "rpt_ent_001.txt"
    if not report_path.exists():
        print(f"Report not found: {report_path}")
        sys.exit(1)

    report_text = report_path.read_text(encoding="utf-8")
    print(f"Parsing: {report_path.name}\n")

    result = await parse_report(report_text)

    print("=== Extracted Report Structure ===")
    print(f"Diagnosis:       {result.diagnosis}")
    print(f"Affected area:   {result.affected_area}")
    print(f"Findings:        {result.findings}")
    print(f"Recommendations: {result.recommendations}")

    combined = " ".join(
        [result.diagnosis, result.affected_area, *result.findings]
    ).lower()
    checks = {
        "Otitis Media": "otitis media" in combined,
        "fluid": "fluid" in combined,
        "middle ear": "middle ear" in combined or "ear" in combined,
    }
    print("\n=== Step 124 Checks ===")
    for label, passed in checks.items():
        print(f"  {label}: {'PASS' if passed else 'FAIL'}")

    if all(checks.values()):
        print("\nDocument agent test PASSED")
    else:
        print("\nDocument agent test PARTIAL — review output above")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
