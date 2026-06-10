import logging
import re

from agent_framework import Agent

from agents.base import get_chat_client, run_agent
from agents.logging_config import log_agent_input, log_agent_output
from agents.prompts import KNOWLEDGE_AGENT_INSTRUCTIONS
from agents.utils import detect_ungrounded_drug_names, extract_citation_markers
from config import AZURE_SEARCH_ENDPOINT, KNOWLEDGE_BASE_NAME, MCP_CONNECTION_NAME

logger = logging.getLogger(__name__)

MCP_ENDPOINT = (
    f"{AZURE_SEARCH_ENDPOINT.rstrip('/')}"
    f"/knowledgebases/{KNOWLEDGE_BASE_NAME}/mcp?api-version=2026-05-01-preview"
)


def _sanitize_ungrounded_drugs(text: str) -> tuple[str, list[str]]:
    remaining = detect_ungrounded_drug_names(text)
    if not remaining:
        return text, []
    sanitized = text
    for drug in remaining:
        sanitized = re.sub(re.escape(drug), "prescribed medication (ask your doctor)", sanitized, flags=re.I)
    return sanitized, detect_ungrounded_drug_names(sanitized)


def _extract_citations(text: str) -> list[str]:
    bracket_cites = extract_citation_markers(text)
    if bracket_cites:
        return bracket_cites
    source_refs = re.findall(r"(?:source|document|reference|citation)[:\s][^\n.]+", text, re.I)
    return source_refs


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

Retrieve grounded medical knowledge from the knowledge base.
You MUST include citation markers like 【source: document_name】 for every fact.
Do not invent drug names or dosages.
"""

    async with Agent(
        client=client,
        name="MedicalKnowledgeAgent",
        instructions=KNOWLEDGE_AGENT_INSTRUCTIONS,
        tools=[mcp_tool],
    ) as agent:
        result = await run_agent(agent, prompt)
        answer_text = result.text
        ungrounded_drugs = detect_ungrounded_drug_names(answer_text)
        if ungrounded_drugs:
            logger.warning(
                "%s | Possible ungrounded drug names: %s — requesting rewrite",
                agent_name,
                ungrounded_drugs,
            )
            rewrite_prompt = f"""
The previous answer mentioned drug names {ungrounded_drugs} without grounded support.
Rewrite WITHOUT any specific drug names or dosages. Keep citations.

Previous answer:
{answer_text}
"""
            rewrite = await run_agent(agent, rewrite_prompt)
            answer_text = rewrite.text
            ungrounded_drugs = detect_ungrounded_drug_names(answer_text)
            if ungrounded_drugs:
                answer_text, ungrounded_drugs = _sanitize_ungrounded_drugs(answer_text)
                logger.warning(
                    "%s | Sanitized remaining drug mentions: %s",
                    agent_name,
                    ungrounded_drugs,
                )

    citations = _extract_citations(answer_text)
    output = {
        "answer": answer_text,
        "citations": citations,
        "ungrounded_drugs": ungrounded_drugs,
    }
    log_agent_output(agent_name, answer=answer_text, citations=citations)
    return output
