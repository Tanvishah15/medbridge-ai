import asyncio
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.knowledge_agent import retrieve_medical_knowledge


async def main() -> None:
    query = "What is Otitis Media?"
    print(f"Query: {query}\n")

    result = await retrieve_medical_knowledge(query)

    answer = result["answer"]
    citations = result["citations"]

    print("=== Answer ===")
    print(answer)
    print("\n=== Citations ===")
    print(citations or "(inline source markers in answer)")

    answer_lower = answer.lower()
    checks = {
        "mentions otitis / middle ear": any(
            term in answer_lower for term in ["otitis", "middle ear", "ear infection"]
        ),
        "has citation markers": bool(citations) or "source" in answer_lower or "†" in answer,
    }

    print("\n=== Step 127-128 Checks ===")
    for label, passed in checks.items():
        print(f"  {label}: {'PASS' if passed else 'FAIL'}")

    if all(checks.values()):
        print("\nKnowledge agent test PASSED")
    else:
        print("\nKnowledge agent test PARTIAL — review output above")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
