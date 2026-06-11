import json
import logging
import re

from pydantic import BaseModel, Field

from agents.base import get_chat_client, run_agent
from agents.models import PatientContext, ReportStructure
from agents.utils import symptoms_are_complete

logger = logging.getLogger(__name__)

PLANNER_INSTRUCTIONS = """
You are the MedBridge Workflow Planner.
Before specialized agents run, decide the execution plan.

Return JSON only:
{
  "needs_clarification": true/false,
  "knowledge_queries": ["query1", "query2"],
  "use_multilingual": true/false,
  "rationale": "one sentence"
}

Rules:
- needs_clarification=true if symptoms lack duration, pain level, or fever status AND no clarification answers yet.
- knowledge_queries: 1-3 focused queries for the medical knowledge agent (symptoms + report diagnosis).
- use_multilingual=true if target language is not English.
"""


class WorkflowPlan(BaseModel):
    needs_clarification: bool = False
    knowledge_queries: list[str] = Field(default_factory=list)
    use_multilingual: bool = False
    rationale: str = ""


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def _rule_based_plan(
    report: ReportStructure,
    patient: PatientContext,
    clarification_answers: list[str] | None,
) -> WorkflowPlan:
    has_answers = bool(clarification_answers)
    needs_clarification = not has_answers and not symptoms_are_complete(patient.symptoms)
    symptoms = patient.symptoms
    if clarification_answers:
        symptoms = f"{symptoms} {' '.join(clarification_answers)}"

    queries = [
        f"{symptoms}. Report diagnosis: {report.diagnosis}",
    ]
    if report.findings:
        queries.append(f"Explain findings {report.findings[0]} for patient context")

    return WorkflowPlan(
        needs_clarification=needs_clarification,
        knowledge_queries=queries[:3],
        use_multilingual=patient.language.lower() != "english",
        rationale="Rule-based plan from symptom completeness and language settings.",
    )


async def plan_workflow(
    report: ReportStructure,
    patient: PatientContext,
    clarification_answers: list[str] | None = None,
) -> WorkflowPlan:
    fallback = _rule_based_plan(report, patient, clarification_answers)

    client = get_chat_client(fast=True)
    agent = client.as_agent(name="WorkflowPlanner", instructions=PLANNER_INSTRUCTIONS)
    prompt = f"""
Report diagnosis: {report.diagnosis}
Report findings: {report.findings}
Patient symptoms: {patient.symptoms}
Language: {patient.language}
Audience: {patient.audience}
Literacy: {patient.literacy_level}
Clarification answers already provided: {bool(clarification_answers)}
Symptoms complete (duration+pain+fever): {symptoms_are_complete(patient.symptoms)}
"""
    try:
        result = await run_agent(agent, prompt)
        data = _parse_json_response(result.text)
        plan = WorkflowPlan(
            needs_clarification=bool(data.get("needs_clarification", fallback.needs_clarification)),
            knowledge_queries=[str(q) for q in data.get("knowledge_queries", fallback.knowledge_queries)][:3],
            use_multilingual=bool(data.get("use_multilingual", fallback.use_multilingual)),
            rationale=str(data.get("rationale", fallback.rationale)),
        )
        if not plan.knowledge_queries:
            plan.knowledge_queries = fallback.knowledge_queries
        return plan
    except Exception as exc:
        logger.warning("WorkflowPlanner failed, using rule-based plan: %s", exc)
        return fallback
