import json
import logging
import re

from agents.base import get_chat_client, run_agent
from agents.logging_config import log_agent_input, log_agent_output
from agents.prompts import DOCUMENT_AGENT_INSTRUCTIONS
from agents.models import ReportStructure

logger = logging.getLogger(__name__)

MIN_REPORT_CHARS = 20


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def _empty_report(message: str) -> ReportStructure:
    return ReportStructure(
        raw_text="",
        diagnosis="No report provided",
        findings=[message],
        affected_area="",
        recommendations=["Provide a valid synthetic demo report."],
    )


async def parse_report(report_text: str) -> ReportStructure:
    agent_name = "DocumentIntelligenceAgent"
    log_agent_input(agent_name, report_text=report_text)

    if not report_text or not report_text.strip():
        empty = _empty_report("Please upload or paste a medical report.")
        log_agent_output(agent_name, diagnosis=empty.diagnosis, findings=empty.findings)
        return empty

    stripped = report_text.strip()
    if len(stripped) < MIN_REPORT_CHARS:
        short = ReportStructure(
            raw_text=report_text,
            diagnosis="Unable to parse report",
            findings=["Input too short or malformed. Please provide a full synthetic report."],
            affected_area="",
            recommendations=["Use demo reports from data/synthetic_reports/"],
        )
        log_agent_output(agent_name, diagnosis=short.diagnosis, findings=short.findings)
        return short

    client = get_chat_client()
    agent = client.as_agent(
        name="DocumentIntelligenceAgent",
        instructions=DOCUMENT_AGENT_INSTRUCTIONS,
    )
    prompt = f"Extract structured data from this report:\n\n{report_text}"
    try:
        result = await run_agent(agent, prompt)
    except Exception as exc:
        logger.warning("%s | LLM call failed: %s", agent_name, exc)
        fallback = ReportStructure(
            raw_text=report_text,
            diagnosis="Unable to parse report",
            findings=[f"Report parsing failed: {exc}"],
            recommendations=["Retry with a clearer synthetic report."],
        )
        log_agent_output(agent_name, diagnosis=fallback.diagnosis, findings=fallback.findings)
        return fallback

    try:
        data = _parse_json_response(result.text)
        report = ReportStructure(**data, raw_text=report_text)
        log_agent_output(
            agent_name,
            diagnosis=report.diagnosis,
            findings=report.findings,
            recommendations=report.recommendations,
        )
        return report
    except Exception:
        logger.warning("%s | JSON parse failed, using fallback", agent_name)
        fallback = ReportStructure(
            raw_text=report_text,
            diagnosis="See report",
            findings=[result.text],
        )
        log_agent_output(agent_name, diagnosis=fallback.diagnosis, findings=fallback.findings)
        return fallback
