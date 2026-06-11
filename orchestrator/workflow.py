import asyncio
import logging
import time
from collections.abc import Callable
from pathlib import Path

from agents.clarification_agent import get_clarification_questions
from agents.document_agent import parse_report
from agents.explanation_agent import generate_explanation
from agents.knowledge_agent import retrieve_medical_knowledge
from agents.logging_config import estimate_tokens, log_agent_input, log_agent_output, log_workflow_metrics
from agents.models import MedBridgeResponse, PatientContext
from agents.multilingual_agent import translate_explanation
from agents.safety_agent import validate_response
from config import MAX_CLARIFICATION_ROUNDS, WORKFLOW_TIMEOUT_SECONDS
from orchestrator.checkpoint import (
    delete_session_checkpoint,
    load_session_checkpoint,
    save_session_checkpoint,
)
from orchestrator.errors import friendly_error_message
from orchestrator.pdf_utils import resolve_report_text
from orchestrator.planner import plan_workflow
from orchestrator.reflection import needs_knowledge_retry, reflect_on_explanation
from orchestrator.trace import ReasoningTrace

logger = logging.getLogger(__name__)

WORKFLOW_NAME = "MedBridgeOrchestrator"

ProgressCallback = Callable[[str], None]


def _notify_progress(callback: ProgressCallback | None, step_key: str) -> None:
    if callback is not None:
        callback(step_key)


def _combined_symptoms(patient: PatientContext, clarification_answers: list[str] | None) -> str:
    if not clarification_answers:
        return patient.symptoms
    extra = " ".join(clarification_answers)
    return f"{patient.symptoms}\nAdditional clarification: {extra}".strip()


async def _retrieve_knowledge(queries: list[str], report_context: str) -> dict:
    if not queries:
        return await retrieve_medical_knowledge("General medical context", report_context)

    combined_answer: list[str] = []
    all_citations: list[str] = []

    for query in queries:
        result = await retrieve_medical_knowledge(query, report_context)
        combined_answer.append(result["answer"])
        all_citations.extend(result.get("citations", []))

    return {
        "answer": "\n\n".join(combined_answer),
        "citations": list(dict.fromkeys(all_citations)),
    }


async def run_medbridge(
    report_text: str,
    patient: PatientContext,
    clarification_answers: list[str] | None = None,
    session_id: str | None = None,
    report_bytes: bytes | None = None,
    report_filename: str = "",
    progress_callback: ProgressCallback | None = None,
) -> MedBridgeResponse:
    started = time.perf_counter()
    trace = ReasoningTrace()
    clarification_round = 0

    if session_id:
        checkpoint = load_session_checkpoint(session_id)
        if checkpoint is None:
            raise ValueError(f"Session checkpoint not found: {session_id}")
        report_text = checkpoint.report_text
        patient = checkpoint.patient
        trace = ReasoningTrace.from_list(checkpoint.trace)
        clarification_round = checkpoint.clarification_round
        if clarification_answers:
            delete_session_checkpoint(session_id)
    else:
        report_text = resolve_report_text(
            report_text=report_text,
            report_bytes=report_bytes,
            filename=report_filename,
        )

    _notify_progress(progress_callback, "reading_report")

    log_agent_input(
        WORKFLOW_NAME,
        report_chars=len(report_text),
        symptoms=patient.symptoms,
        language=patient.language,
        clarification_answers=clarification_answers,
    )

    report = await parse_report(report_text)
    trace.add(
        "DocumentIntelligence",
        {
            "diagnosis": report.diagnosis,
            "findings": report.findings,
            "affected_area": report.affected_area,
        },
    )

    _notify_progress(progress_callback, "checking_symptoms")

    plan = await plan_workflow(report, patient, clarification_answers)
    trace.add(
        "Planner",
        {
            "needs_clarification": plan.needs_clarification,
            "knowledge_queries": plan.knowledge_queries,
            "use_multilingual": plan.use_multilingual,
            "rationale": plan.rationale,
        },
    )

    questions = await get_clarification_questions(report, patient)
    if plan.needs_clarification and questions and not clarification_answers:
        if clarification_round >= MAX_CLARIFICATION_ROUNDS:
            trace.add(
                "Clarification",
                {
                    "questions": questions,
                    "skipped": True,
                    "reason": "max_rounds_reached",
                    "max_rounds": MAX_CLARIFICATION_ROUNDS,
                },
            )
        else:
            next_round = clarification_round + 1
            trace.add(
                "Clarification",
                {"questions": questions, "skipped": False, "planner_triggered": True, "round": next_round},
            )
            sid = save_session_checkpoint(
                report_text=report_text,
                patient=patient,
                trace=trace.to_list(),
                clarification_questions=questions,
                session_id=session_id,
                clarification_round=next_round,
            )
            response = MedBridgeResponse(
                explanation="",
                clarification_needed=True,
                clarification_questions=questions,
                trace=trace.to_list(),
                session_id=sid,
            )
            log_agent_output(
                WORKFLOW_NAME,
                clarification_needed=True,
                clarification_questions=questions,
                trace_steps=len(response.trace),
                clarification_round=next_round,
            )
            _log_run_metrics(started, report_text, response)
            return response

    if not (plan.needs_clarification and questions and not clarification_answers):
        trace.add(
            "Clarification",
            {"questions": questions, "skipped": True, "planner_triggered": plan.needs_clarification},
        )

    symptoms = _combined_symptoms(patient, clarification_answers)
    _notify_progress(progress_callback, "retrieving_knowledge")
    knowledge = await _retrieve_knowledge(plan.knowledge_queries, report.model_dump_json())
    trace.add(
        "MedicalKnowledge",
        {
            "queries": plan.knowledge_queries,
            "answer": knowledge["answer"],
            "citations": knowledge.get("citations", []),
        },
    )

    _notify_progress(progress_callback, "explaining")
    explanation = await generate_explanation(
        report_summary=report.model_dump_json(),
        knowledge=knowledge["answer"],
        symptoms=symptoms,
        literacy_level=patient.literacy_level,
        output_language="English",
        audience=patient.audience,
    )
    trace.add("PatientExplanation", explanation)

    reflection = await reflect_on_explanation(
        explanation,
        knowledge["answer"],
        symptoms,
        report,
        patient,
    )
    trace.add(
        "SelfReflection",
        {
            "grounded": reflection.grounded,
            "confidence": reflection.confidence,
            "missing_topics": reflection.missing_topics,
            "follow_up_query": reflection.follow_up_query,
        },
    )

    if needs_knowledge_retry(reflection):
        extra = await retrieve_medical_knowledge(
            reflection.follow_up_query,
            report.model_dump_json(),
        )
        knowledge["answer"] = f"{knowledge['answer']}\n\n{extra['answer']}".strip()
        knowledge["citations"] = list(
            dict.fromkeys(knowledge.get("citations", []) + extra.get("citations", []))
        )
        trace.add(
            "MedicalKnowledgeRetry",
            {
                "query": reflection.follow_up_query,
                "answer": extra["answer"],
                "citations": extra.get("citations", []),
            },
        )
        explanation = await generate_explanation(
            report_summary=report.model_dump_json(),
            knowledge=knowledge["answer"],
            symptoms=symptoms,
            literacy_level=patient.literacy_level,
            output_language="English",
            audience=patient.audience,
        )
        trace.add("PatientExplanationRetry", explanation)

        retry_reflection = await reflect_on_explanation(
            explanation,
            knowledge["answer"],
            symptoms,
            report,
            patient,
        )
        trace.add(
            "SelfReflectionRetry",
            {
                "grounded": retry_reflection.grounded,
                "confidence": retry_reflection.confidence,
                "missing_topics": retry_reflection.missing_topics,
            },
        )

    _notify_progress(progress_callback, "validating_safety")
    if plan.use_multilingual:
        explanation = await translate_explanation(
            explanation,
            patient.language,
            patient.audience,
        )
        trace.add(
            "Multilingual",
            {"language": patient.language, "audience": patient.audience, "text": explanation},
        )

    safety = await validate_response(explanation)
    final = safety.get("revised_response", explanation)
    trace.add(
        "Safety",
        {
            "safe": safety.get("safe", True),
            "issues": safety.get("issues", []),
            "revised_response": final,
        },
    )

    response = MedBridgeResponse(
        explanation=final,
        citations=knowledge.get("citations", []),
        clarification_needed=False,
        safety_passed=safety.get("safe", True),
        safety_notes=safety.get("issues", []),
        trace=trace.to_list(),
    )
    log_agent_output(
        WORKFLOW_NAME,
        clarification_needed=False,
        safety_passed=response.safety_passed,
        explanation=final,
        citations=response.citations,
        trace_steps=len(response.trace),
    )
    _log_run_metrics(started, report_text, response)
    return response


def _log_run_metrics(started: float, report_text: str, response: MedBridgeResponse) -> None:
    trace_text = " ".join(str(step.get("output", "")) for step in response.trace)
    log_workflow_metrics(
        WORKFLOW_NAME,
        duration_seconds=time.perf_counter() - started,
        trace_steps=len(response.trace),
        report_chars=len(report_text),
        explanation_chars=len(response.explanation),
        estimated_tokens=estimate_tokens(report_text, trace_text, response.explanation),
    )


async def run_medbridge_safe(
    report_text: str,
    patient: PatientContext,
    clarification_answers: list[str] | None = None,
    session_id: str | None = None,
    report_bytes: bytes | None = None,
    report_filename: str = "",
    progress_callback: ProgressCallback | None = None,
) -> MedBridgeResponse:
    """Step 198/201 — catch workflow failures and enforce total timeout."""
    try:
        return await asyncio.wait_for(
            run_medbridge(
                report_text,
                patient,
                clarification_answers=clarification_answers,
                session_id=session_id,
                report_bytes=report_bytes,
                report_filename=report_filename,
                progress_callback=progress_callback,
            ),
            timeout=WORKFLOW_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError as exc:
        logger.exception("%s | workflow timed out after %ss", WORKFLOW_NAME, WORKFLOW_TIMEOUT_SECONDS)
        message = friendly_error_message(exc)
        trace = ReasoningTrace()
        trace.add(
            "Error",
            {
                "error_type": "TimeoutError",
                "detail": f"Exceeded {WORKFLOW_TIMEOUT_SECONDS}s workflow limit",
                "message": message,
            },
        )
        return MedBridgeResponse(
            explanation="",
            clarification_needed=False,
            safety_passed=False,
            safety_notes=[message],
            trace=trace.to_list(),
            error=True,
            error_message=message,
        )
    except Exception as exc:
        logger.exception("%s | workflow failed", WORKFLOW_NAME)
        message = friendly_error_message(exc)
        trace = ReasoningTrace()
        trace.add(
            "Error",
            {
                "error_type": type(exc).__name__,
                "detail": str(exc),
                "message": message,
            },
        )
        return MedBridgeResponse(
            explanation="",
            clarification_needed=False,
            safety_passed=False,
            safety_notes=[message],
            trace=trace.to_list(),
            error=True,
            error_message=message,
        )


async def _cli_demo() -> None:
    """Step 208/209 — quick CLI smoke test for orchestrator.workflow."""
    import sys

    from dotenv import load_dotenv

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    load_dotenv()

    root = Path(__file__).resolve().parent.parent
    report_path = root / "data" / "synthetic_reports" / "rpt_ent_001.txt"
    report = report_path.read_text(encoding="utf-8")
    patient = PatientContext(
        symptoms="Mere kaan mein 3 din se ras aa rahi hai. Yeh report samjhao.",
        language="Hindi",
        literacy_level="simple",
        audience="patient",
    )

    print("=== MedBridge workflow CLI (Step 209) ===")
    print(f"Report: {report_path.name}")
    round1 = await run_medbridge_safe(report, patient)
    print("Clarification needed:", round1.clarification_needed)
    if round1.clarification_questions:
        print("Questions:", round1.clarification_questions)

    if round1.clarification_needed and round1.session_id:
        round2 = await run_medbridge_safe(
            "",
            patient,
            clarification_answers=["Haan, halka bukhar hai. Kaan mein dard bhi hai."],
            session_id=round1.session_id,
        )
        print("\nExplanation preview:")
        print(round2.explanation[:400], "...")
        print("Safety passed:", round2.safety_passed)
        print("Trace steps:", len(round2.trace))


if __name__ == "__main__":
    asyncio.run(_cli_demo())
