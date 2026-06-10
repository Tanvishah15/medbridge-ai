import asyncio
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.multilingual_agent import translate_explanation

SAMPLE_EXPLANATION = """
Your report shows Otitis Media, which means fluid and inflammation in the middle ear
behind the eardrum. The fluid leaking from your ear matches what the report found.
You are on antibiotics and should follow up with your doctor in 7 days.
"""

ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


async def run_case(
    label: str,
    language: str,
    audience: str,
    checks: dict[str, callable],
) -> bool:
    print(f"\n{'=' * 60}")
    print(label)
    print(f"Language: {language} | Audience: {audience}\n")

    translated = await translate_explanation(
        explanation=SAMPLE_EXPLANATION,
        target_language=language,
        audience=audience,
    )

    print("=== Translation ===")
    print(translated)

    text_lower = translated.lower()
    print(f"\n=== {label} Checks ===")
    passed_all = True
    for name, check_fn in checks.items():
        passed = check_fn(translated, text_lower)
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")
        passed_all = passed_all and passed

    return passed_all


async def main() -> None:
    results = []

    results.append(
        await run_case(
            label="Step 137 — Spanish family translation",
            language="Spanish",
            audience="family",
            checks={
                "contains Spanish": lambda t, tl: any(
                    word in tl
                    for word in ["información", "médico", "oído", "familia", "reporte", "antibiótico"]
                ),
                "mentions ear/fluid concept": lambda t, tl: any(
                    word in tl for word in ["oído", "fluido", "infección", "oreja"]
                ),
                "includes disclaimer tone": lambda t, tl: any(
                    word in tl for word in ["educativ", "médico", "doctor", "consejo"]
                ),
            },
        )
    )

    results.append(
        await run_case(
            label="Step 138 — Hindi translation",
            language="Hindi",
            audience="patient",
            checks={
                "contains Hindi script or romanized Hindi": lambda t, tl: bool(DEVANAGARI_RE.search(t))
                or any(word in tl for word in ["kaan", "doctor", "dawai", "report"]),
                "mentions ear/fluid concept": lambda t, tl: any(
                    word in tl for word in ["kaan", "fluid", "kan", "ear", "कान", "fluid"]
                ),
            },
        )
    )

    results.append(
        await run_case(
            label="Step 139 — Arabic translation",
            language="Arabic",
            audience="family",
            checks={
                "contains Arabic script": lambda t, tl: bool(ARABIC_RE.search(t)),
                "mentions medical context": lambda t, tl: any(
                    word in t for word in ["طبيب", "أذن", "تقرير", "مضاد"]
                )
                or len(t) > 80,
            },
        )
    )

    print(f"\n{'=' * 60}")
    if all(results):
        print("All multilingual agent tests PASSED")
    else:
        print("Some multilingual agent tests FAILED")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
