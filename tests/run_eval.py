"""Step 234 — MedBridge evaluation runner and scoring logic."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv()

from agents.models import MedBridgeResponse
from tests.language_parity import PARITY_CASE_IDS, compare_parity_suite

EVAL_FILE = Path(__file__).resolve().parent / "eval_cases.json"
REPORTS_DIR = ROOT / "data" / "synthetic_reports"
RESULTS_FILE = Path(__file__).resolve().parent / "eval_results.json"

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
GUJARATI_RE = re.compile(r"[\u0A80-\u0AFF]")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
SPANISH_HINTS = ("glucosa", "azúcar", "azucar", "médico", "medico", "información", "consulte", "aviso")
FRENCH_HINTS = ("médecin", "medecin", "consultez", "avis", "information", "santé", "sante", "pas un avis")
GERMAN_HINTS = ("arzt", "ärzt", "beratung", "hinweis", "informationen", "bitte konsultieren", "medizin")


@dataclass
class CaseResult:
    case_id: str
    name: str
    passed: bool
    score_pct: float
    criteria: dict[str, bool] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    error: bool = False


def load_eval_cases(path: Path | None = None) -> dict:
    return json.loads((path or EVAL_FILE).read_text(encoding="utf-8"))


def load_report_text(report_file: str) -> str:
    path = REPORTS_DIR / report_file
    if not path.exists():
        raise FileNotFoundError(f"Report not found: {path}")
    return path.read_text(encoding="utf-8")


def _trace_agents(result: MedBridgeResponse) -> list[str]:
    return [step.get("agent", "") for step in result.trace]


def _text_has_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term.lower() in lower or term in text for term in terms)


def _check_language(text: str, language: str) -> tuple[bool, str]:
    lang = language.lower()
    if lang == "hindi":
        if DEVANAGARI_RE.search(text) or _text_has_any(text, ["kaan", "bukhar", "dard"]):
            return True, ""
        return False, "Expected Hindi (Devanagari or common Hindi terms)"
    if lang == "spanish":
        lower = text.lower()
        if any(term in lower for term in SPANISH_HINTS) or "¿" in text or "á" in lower or "é" in lower:
            return True, ""
        return False, "Expected Spanish vocabulary or accents"
    if lang == "arabic":
        if ARABIC_RE.search(text):
            return True, ""
        return False, "Expected Arabic script in explanation"
    if lang == "chinese":
        if CJK_RE.search(text):
            return True, ""
        return False, "Expected Chinese characters in explanation"
    if lang == "french":
        lower = text.lower()
        if any(term in lower for term in FRENCH_HINTS) or "é" in lower or "à" in lower:
            return True, ""
        return False, "Expected French vocabulary or accents"
    if lang == "german":
        lower = text.lower()
        if any(term in lower for term in GERMAN_HINTS) or "ü" in lower or "ä" in lower or "ß" in lower:
            return True, ""
        return False, "Expected German vocabulary or umlauts"
    if lang == "gujarati":
        if GUJARATI_RE.search(text):
            return True, ""
        return False, "Expected Gujarati script in explanation"
    if lang == "english":
        if len(text.strip()) > 0:
            return True, ""
        return False, "Expected non-empty English explanation"
    return True, ""


def _check_grounding(result: MedBridgeResponse, expects: dict) -> tuple[bool, list[str]]:
    failures: list[str] = []
    grounding = expects.get("grounding", {})
    text = result.explanation.lower()
    agents = _trace_agents(result)

    if grounding.get("trace_agent"):
        agent = grounding["trace_agent"]
        if agent not in agents:
            failures.append(f"Missing trace agent: {agent}")

    if grounding.get("citations_or_doctor"):
        has_cite = bool(result.citations)
        has_doctor = _text_has_any(text, ["doctor", "healthcare", "médico", "medico", "consult", "डॉक्टर"])
        if not (has_cite or has_doctor):
            failures.append("Expected citations or consult-doctor wording")

    report_terms = expects.get("report_terms_any", [])
    if report_terms and not _text_has_any(result.explanation, report_terms):
        failures.append(f"Expected report term in explanation: {report_terms[:3]}…")

    return len(failures) == 0, failures


def _contains_forbidden_phrase(text: str, phrase: str) -> bool:
    """Match multi-word phrases as substrings; single words use word boundaries."""
    lower = text.lower()
    phrase_lower = phrase.lower()
    if " " in phrase_lower:
        return phrase_lower in lower
    return bool(re.search(rf"\b{re.escape(phrase_lower)}\b", lower))


def _check_safety(result: MedBridgeResponse, expects: dict) -> tuple[bool, list[str]]:
    failures: list[str] = []
    text = result.explanation.lower()

    if expects.get("safety_passed") is True and not result.safety_passed:
        failures.append("safety_passed is False")

    for phrase in expects.get("forbidden_phrases", []):
        if _contains_forbidden_phrase(text, phrase):
            failures.append(f"Forbidden phrase found: {phrase!r}")

    must_include = expects.get("must_include_any", [])
    if must_include and not _text_has_any(text, must_include):
        failures.append(f"Expected safety redirect phrase: {must_include}")

    return len(failures) == 0, failures


def _check_clarification(result: MedBridgeResponse, expects: dict) -> tuple[bool, list[str]]:
    failures: list[str] = []
    expected = expects.get("clarification_needed")

    if expected is not None and result.clarification_needed != expected:
        failures.append(
            f"clarification_needed={result.clarification_needed}, expected {expected}"
        )

    if expects.get("explanation_empty") and result.explanation.strip():
        failures.append("Expected empty explanation during clarification round")

    q_min = expects.get("clarification_questions_min")
    q_max = expects.get("clarification_questions_max")
    q_count = len(result.clarification_questions)
    if q_min is not None and q_count < q_min:
        failures.append(f"Too few clarification questions: {q_count} < {q_min}")
    if q_max is not None and q_count > q_max:
        failures.append(f"Too many clarification questions: {q_count} > {q_max}")

    for agent in expects.get("agents_required", []):
        if agent not in _trace_agents(result):
            failures.append(f"Missing required agent: {agent}")

    return len(failures) == 0, failures


def _check_multilingual(result: MedBridgeResponse, expects: dict) -> tuple[bool, list[str]]:
    language = expects.get("language")
    if not language:
        return True, []
    ok, reason = _check_language(result.explanation, language)
    return ok, [] if ok else [reason]


def _check_symptom_match(result: MedBridgeResponse, expects: dict) -> tuple[bool, list[str]]:
    terms = expects.get("symptom_terms_any", [])
    if not terms:
        return True, []
    if _text_has_any(result.explanation, terms):
        return True, []
    return False, [f"Expected symptom connection terms: {terms[:4]}…"]


def _check_basic(result: MedBridgeResponse, expects: dict) -> list[str]:
    failures: list[str] = []
    if result.error:
        failures.append(result.error_message or "Workflow returned error")

    min_len = expects.get("explanation_min_length")
    if min_len is not None and len(result.explanation.strip()) < min_len:
        failures.append(f"Explanation too short: {len(result.explanation)} < {min_len}")

    for agent in expects.get("agents_required", []):
        if agent not in _trace_agents(result):
            failures.append(f"Missing required agent: {agent}")

    return failures


def score_result(result: MedBridgeResponse, expects: dict) -> tuple[dict[str, bool], list[str]]:
    """Score a workflow result against case expectations."""
    criteria_flags = expects.get("criteria", {})
    scores: dict[str, bool] = {}
    all_failures: list[str] = []

    basic_failures = _check_basic(result, expects)
    if basic_failures:
        all_failures.extend(basic_failures)

    checkers = {
        "clarification": lambda: _check_clarification(result, expects),
        "safety": lambda: _check_safety(result, expects),
        "grounding": lambda: _check_grounding(result, expects),
        "multilingual": lambda: _check_multilingual(result, expects),
        "symptom_match": lambda: _check_symptom_match(result, expects),
    }

    for name, enabled in criteria_flags.items():
        if not enabled:
            continue
        checker = checkers.get(name)
        if checker is None:
            continue
        passed, failures = checker()
        scores[name] = passed and not basic_failures
        if not passed:
            all_failures.extend(failures)

    if not criteria_flags and expects.get("clarification_needed") is not None:
        passed, failures = _check_clarification(result, expects)
        scores["clarification"] = passed and not basic_failures
        if not passed:
            all_failures.extend(failures)

    return scores, all_failures


async def run_case(case: dict) -> tuple[MedBridgeResponse, float]:
    from agents.models import PatientContext
    from orchestrator.workflow import run_medbridge

    report = load_report_text(case["report_file"])
    patient_data = case["patient"]
    patient = PatientContext(
        symptoms=patient_data["symptoms"],
        language=patient_data["language"],
        literacy_level=patient_data["literacy_level"],
        audience=patient_data["audience"],
    )
    answers = case.get("clarification_answers")

    started = time.perf_counter()
    result = await run_medbridge(
        report,
        patient,
        clarification_answers=answers,
    )
    duration = time.perf_counter() - started
    return result, duration


def evaluate_case(case: dict, result: MedBridgeResponse, duration: float) -> CaseResult:
    scores, failures = score_result(result, case["expects"])
    if scores:
        passed_count = sum(1 for value in scores.values() if value)
        score_pct = round(100 * passed_count / len(scores), 1)
        passed = passed_count == len(scores) and not result.error
    else:
        score_pct = 0.0 if result.error else 100.0
        passed = not result.error and not failures

    return CaseResult(
        case_id=case["id"],
        name=case["name"],
        passed=passed and not failures,
        score_pct=score_pct,
        criteria=scores,
        failures=failures,
        duration_seconds=round(duration, 1),
        error=result.error,
    )


async def run_eval_suite(
    case_ids: list[str] | None = None,
) -> tuple[list[CaseResult], float]:
    data = load_eval_cases()
    cases = data["cases"]
    if case_ids:
        cases = [case for case in cases if case["id"] in case_ids]
        if not cases:
            raise ValueError(f"No matching cases: {case_ids}")

    results: list[CaseResult] = []
    for case in cases:
        workflow_result, duration = await run_case(case)
        results.append(evaluate_case(case, workflow_result, duration))

    if results:
        suite_score = round(sum(r.score_pct for r in results) / len(results), 1)
    else:
        suite_score = 0.0
    return results, suite_score


def format_report(results: list[CaseResult], suite_score: float) -> str:
    lines = [
        "",
        "MedBridge Eval Report (Step 234)",
        "=" * 40,
        f"Suite score: {suite_score}%  (target >= 80%)",
        "",
    ]
    for item in results:
        status = "PASS" if item.passed else "FAIL"
        lines.append(f"[{status}] {item.case_id} — {item.name} ({item.score_pct}%, {item.duration_seconds}s)")
        for criterion, ok in item.criteria.items():
            mark = "OK" if ok else "X"
            lines.append(f"    {mark} {criterion}")
        for failure in item.failures:
            lines.append(f"    ! {failure}")
        lines.append("")
    return "\n".join(lines)


def save_results(results: list[CaseResult], suite_score: float, output: Path) -> None:
    payload = {
        "suite_score": suite_score,
        "case_count": len(results),
        "passed_count": sum(1 for r in results if r.passed),
        "cases": [
            {
                "id": r.case_id,
                "name": r.name,
                "passed": r.passed,
                "score_pct": r.score_pct,
                "criteria": r.criteria,
                "failures": r.failures,
                "duration_seconds": r.duration_seconds,
                "error": r.error,
            }
            for r in results
        ],
    }
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Run MedBridge eval cases (Step 234–235).")
    parser.add_argument("--case", action="append", help="Run specific case id (repeatable)")
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS_FILE,
        help=f"Write JSON results (default: {RESULTS_FILE.name})",
    )
    parser.add_argument("--dry-run", action="store_true", help="List cases only; no Azure calls")
    parser.add_argument(
        "--parity",
        action="store_true",
        help="Step 241: run Hindi/Spanish/Arabic parity cases (eval_002–004)",
    )
    args = parser.parse_args(argv)

    if args.parity:
        args.case = list(PARITY_CASE_IDS)

    data = load_eval_cases()
    cases = data["cases"]
    if args.case:
        cases = [c for c in cases if c["id"] in args.case]

    if args.dry_run:
        print(f"Eval cases: {len(cases)}")
        for case in cases:
            print(f"  {case['id']}: {case['name']}")
        return 0

    try:
        import agent_framework  # noqa: F401
    except ModuleNotFoundError:
        print("Missing dependencies. Activate the project venv first:")
        print("  .venv\\Scripts\\Activate.ps1")
        return 1

    from config import azure_configured

    if not azure_configured():
        print("Azure not configured. Add AZURE_AI_PROJECT_ENDPOINT to .env and retry.")
        return 1

    print(f"Running {len(cases)} eval case(s)…")
    results, suite_score = asyncio.run(run_eval_suite([c["id"] for c in cases]))
    print(format_report(results, suite_score))

    exit_code = 0
    if args.parity:
        parity_ok, parity_failures = compare_parity_suite(results)
        print("")
        print("Language parity (Step 241)")
        print("=" * 40)
        if parity_ok:
            print("PASS — Hindi, Spanish, and Arabic meet the same quality bar.")
        else:
            print("FAIL — parity gaps detected:")
            for item in parity_failures:
                print(f"  ! {item}")
            exit_code = 1

    save_results(results, suite_score, args.output)
    print(f"Results saved to {args.output}")
    if exit_code:
        return exit_code
    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
