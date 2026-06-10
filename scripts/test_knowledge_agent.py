import asyncio
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.knowledge_agent import retrieve_medical_knowledge


async def run_test(query: str, checks: dict[str, callable], label: str) -> bool:
    print(f"\n{'=' * 60}")
    print(f"{label}")
    print(f"Query: {query}\n")

    result = await retrieve_medical_knowledge(query)
    answer = result["answer"]
    citations = result["citations"]

    print("=== Answer ===")
    print(answer)
    print("\n=== Citations ===")
    print(citations or "(inline source markers in answer)")

    answer_lower = answer.lower()
    print(f"\n=== {label} Checks ===")
    passed_all = True
    for name, check_fn in checks.items():
        passed = check_fn(answer_lower, citations)
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")
        passed_all = passed_all and passed

    return passed_all


async def main() -> None:
    results = []

    results.append(
        await run_test(
            query="What is Otitis Media?",
            label="Step 127-128 — Otitis Media",
            checks={
                "mentions otitis / middle ear": lambda a, c: any(
                    term in a for term in ["otitis", "middle ear", "ear infection"]
                ),
                "has citation markers": lambda a, c: bool(c) or "source" in a or "†" in a,
            },
        )
    )

    results.append(
        await run_test(
            query="Why would ear discharge match a report showing middle ear fluid?",
            label="Step 129 — Symptom connection",
            checks={
                "mentions ear discharge": lambda a, c: "discharge" in a or "drainage" in a,
                "mentions middle ear fluid": lambda a, c: "middle ear" in a and "fluid" in a,
                "explains connection": lambda a, c: any(
                    term in a for term in ["infection", "otitis", "leak", "buildup", "accumulation"]
                ),
                "has citation markers": lambda a, c: bool(c) or "source" in a or "†" in a,
            },
        )
    )

    print(f"\n{'=' * 60}")
    if all(results):
        print("All knowledge agent tests PASSED")
    else:
        print("Some knowledge agent tests FAILED")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
