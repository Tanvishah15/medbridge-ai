import logging

from agents.clarification_agent import get_clarification_questions
from agents.document_agent import parse_report
from agents.explanation_agent import generate_explanation
from agents.knowledge_agent import retrieve_medical_knowledge
from agents.logging_config import log_agent_input, log_agent_output
from agents.models import MedBridgeResponse, PatientContext
from agents.multilingual_agent import translate_explanation
from agents.safety_agent import validate_response
from orchestrator.checkpoint import (
    delete_session_checkpoint,
    load_session_checkpoint,
    save_session_checkpoint,
)
from orchestrator.planner import plan_workflow
from orchestrator.reflection import needs_knowledge_retry, reflect_on_explanation
from orchestrator.trace import ReasoningTrace

logger = logging.getLogger(__name__)

WORKFLOW_NAME = "MedBridgeOrchestrator"


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
) -> MedBridgeResponse:
    trace = ReasoningTrace()

    if session_id:
        checkpoint = load_session_checkpoint(session_id)
        if checkpoint is None:
            raise ValueError(f"Session checkpoint not found: {session_id}")
        report_text = checkpoint.report_text
        patient = checkpoint.patient
        trace = ReasoningTrace.from_list(checkpoint.trace)
        if clarification_answers:
            delete_session_checkpoint(session_id)

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
        trace.add(
            "Clarification",
            {"questions": questions, "skipped": False, "planner_triggered": True},
        )
        sid = save_session_checkpoint(
            report_text=report_text,
            patient=patient,
            trace=trace.to_list(),
            clarification_questions=questions,
            session_id=session_id,
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
        )
        return response

    trace.add(
        "Clarification",
        {"questions": questions, "skipped": True, "planner_triggered": plan.needs_clarification},
    )

    symptoms = _combined_symptoms(patient, clarification_answers)
    knowledge = await _retrieve_knowledge(plan.knowledge_queries, report.model_dump_json())
    trace.add(
        "MedicalKnowledge",
        {
            "queries": plan.knowledge_queries,
            "answer": knowledge["answer"],
            "citations": knowledge.get("citations", []),
        },
    )

    explanation = await generate_explanation(
        report_summary=report.model_dump_json(),
        knowledge=knowledge["answer"],
        symptoms=symptoms,
        literacy_level=patient.literacy_level,
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
    return response
