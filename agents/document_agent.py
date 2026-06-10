import json
import re

from agents.base import get_chat_client
from agents.prompts import DOCUMENT_AGENT_INSTRUCTIONS
from agents.models import ReportStructure


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def parse_report(report_text: str) -> ReportStructure:
    client = get_chat_client()
    agent = client.as_agent(
        name="DocumentIntelligenceAgent",
        instructions=DOCUMENT_AGENT_INSTRUCTIONS,
    )
    prompt = f"Extract structured data from this report:\n\n{report_text}"
    result = await agent.run(prompt)
    try:
        data = _parse_json_response(result.text)
        return ReportStructure(**data, raw_text=report_text)
    except Exception:
        return ReportStructure(raw_text=report_text, diagnosis="See report", findings=[result.text])
