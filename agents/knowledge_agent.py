import logging
import re

from agent_framework import Agent

from agents.base import get_chat_client
from agents.logging_config import log_agent_input, log_agent_output
from agents.prompts import KNOWLEDGE_AGENT_INSTRUCTIONS
from config import AZURE_SEARCH_ENDPOINT, KNOWLEDGE_BASE_NAME, MCP_CONNECTION_NAME

logger = logging.getLogger(__name__)

MCP_ENDPOINT = (
    f"{AZURE_SEARCH_ENDPOINT.rstrip('/')}"
    f"/knowledgebases/{KNOWLEDGE_BASE_NAME}/mcp?api-version=2026-05-01-preview"
)


def _extract_citations(text: str) -> list[str]:
    return re.findall(r"【[^】]+】", text)


async def retrieve_medical_knowledge(query: str, report_context: str = "") -> dict:
    agent_name = "MedicalKnowledgeAgent"
    log_agent_input(agent_name, query=query, report_context=report_context)
    client = get_chat_client()
    mcp_tool = client.get_mcp_tool(
        name="medbridge_knowledge_base",
        url=MCP_ENDPOINT,
        project_connection_id=MCP_CONNECTION_NAME,
        allowed_tools=["knowledge_base_retrieve"],
        approval_mode="never_require",
    )

    prompt = f"""
Patient context: {report_context}
Query: {query}
Retrieve grounded medical knowledge. Include citations.
"""

    async with Agent(
        client=client,
        name="MedicalKnowledgeAgent",
        instructions=KNOWLEDGE_AGENT_INSTRUCTIONS,
        tools=[mcp_tool],
    ) as agent:
        result = await agent.run(prompt)

    citations = _extract_citations(result.text)
    output = {"answer": result.text, "citations": citations}
    log_agent_output(agent_name, answer=result.text, citations=citations)
    return output
