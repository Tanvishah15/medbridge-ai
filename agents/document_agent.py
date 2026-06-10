import json
import logging
import re

from agents.base import get_chat_client
from agents.logging_config import log_agent_input, log_agent_output
from agents.prompts import DOCUMENT_AGENT_INSTRUCTIONS
from agents.models import ReportStructure

logger = logging.getLogger(__name__)


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def parse_report(report_text: str) -> ReportStructure:
    agent_name = "DocumentIntelligenceAgent"
    log_agent_input(agent_name, report_text=report_text)
    client = get_chat_client()
    agent = client.as_agent(
        name="DocumentIntelligenceAgent",
        instructions=DOCUMENT_AGENT_INSTRUCTIONS,
    )
    prompt = f"Extract structured data from this report:\n\n{report_text}"
    result = await agent.run(prompt)
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
        fallback = ReportStructure(raw_text=report_text, diagnosis="See report", findings=[result.text])
        log_agent_output(agent_name, diagnosis=fallback.diagnosis, findings=fallback.findings)
        return fallback
