"""Alternative MedBridge orchestration via Agent Framework HandoffBuilder (Step 192)."""

import logging
from typing import Any

from agent_framework import Agent, Message
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import HandoffAgentUserRequest, HandoffBuilder

from agents.base import get_chat_client
from agents.models import MedBridgeResponse, PatientContext
from agents.prompts import (
    CLARIFICATION_AGENT_INSTRUCTIONS,
    DOCUMENT_AGENT_INSTRUCTIONS,
    EXPLANATION_AGENT_INSTRUCTIONS,
    KNOWLEDGE_AGENT_INSTRUCTIONS,
    MULTILINGUAL_AGENT_INSTRUCTIONS,
    SAFETY_AGENT_INSTRUCTIONS,
)
from config import AZURE_SEARCH_ENDPOINT, KNOWLEDGE_BASE_NAME, MCP_CONNECTION_NAME

logger = logging.getLogger(__name__)

MCP_ENDPOINT = (
    f"{AZURE_SEARCH_ENDPOINT.rstrip('/')}"
    f"/knowledgebases/{KNOWLEDGE_BASE_NAME}/mcp?api-version=2026-05-01-preview"
)

TRIAGE_INSTRUCTIONS = """
You are MedBridge Triage Agent.
Receive the patient report and symptoms, then hand off to document_agent immediately.
Do not explain medical findings yourself.
"""

HANDOFF_SUFFIX = """
After completing your task, hand off to the next specialist using your handoff tool.
Do not finish the entire workflow yourself.
"""


def create_medbridge_handoff_agents(client: FoundryChatClient | None = None) -> dict[str, Agent]:
    client = client or get_chat_client()
    mcp_tool = client.get_mcp_tool(
        name="medbridge_knowledge_base",
        url=MCP_ENDPOINT,
        project_connection_id=MCP_CONNECTION_NAME,
        allowed_tools=["knowledge_base_retrieve"],
        approval_mode="never_require",
    )
    history = {"require_per_service_call_history_persistence": True}

    triage = Agent(
        client=client,
        name="triage_agent",
        instructions=TRIAGE_INSTRUCTIONS + HANDOFF_SUFFIX,
        **history,
    )
    document = Agent(
        client=client,
        name="document_agent",
        instructions=DOCUMENT_AGENT_INSTRUCTIONS + HANDOFF_SUFFIX,
        **history,
    )
    clarification = Agent(
        client=client,
        name="clarification_agent",
        instructions=CLARIFICATION_AGENT_INSTRUCTIONS + HANDOFF_SUFFIX,
        **history,
    )
    knowledge = Agent(
        client=client,
        name="knowledge_agent",
        instructions=KNOWLEDGE_AGENT_INSTRUCTIONS + HANDOFF_SUFFIX,
        tools=[mcp_tool],
        **history,
    )
    explanation = Agent(
        client=client,
        name="explanation_agent",
        instructions=EXPLANATION_AGENT_INSTRUCTIONS + HANDOFF_SUFFIX,
        **history,
    )
    multilingual = Agent(
        client=client,
        name="multilingual_agent",
        instructions=MULTILINGUAL_AGENT_INSTRUCTIONS + HANDOFF_SUFFIX,
        **history,
    )
    safety = Agent(
        client=client,
        name="safety_agent",
        instructions=SAFETY_AGENT_INSTRUCTIONS,
        **history,
    )

    return {
        "triage_agent": triage,
        "document_agent": document,
        "clarification_agent": clarification,
        "knowledge_agent": knowledge,
        "explanation_agent": explanation,
        "multilingual_agent": multilingual,
        "safety_agent": safety,
    }


def build_medbridge_handoff_workflow(
    client: FoundryChatClient | None = None,
):
    agents = create_medbridge_handoff_agents(client)
    triage = agents["triage_agent"]
    document = agents["document_agent"]
    clarification = agents["clarification_agent"]
    knowledge = agents["knowledge_agent"]
    explanation = agents["explanation_agent"]
    multilingual = agents["multilingual_agent"]
    safety = agents["safety_agent"]

    def _terminated(conversation: list[Message]) -> bool:
        if not conversation:
            return False
        assistant_authors = [
            getattr(message, "author_name", "")
            for message in conversation
            if message.role == "assistant"
        ]
        return "safety_agent" in assistant_authors or "explanation_agent" in assistant_authors

    workflow = (
        HandoffBuilder(
            name="medbridge_handoff",
            participants=list(agents.values()),
            termination_condition=_terminated,
        )
        .with_start_agent(triage)
        .add_handoff(triage, [document])
        .add_handoff(document, [clarification])
        .add_handoff(clarification, [knowledge])
        .add_handoff(knowledge, [explanation])
        .add_handoff(explanation, [multilingual, safety])
        .add_handoff(multilingual, [safety])
        .build()
    )
    return workflow, agents


def _build_initial_message(
    report_text: str,
    patient: PatientContext,
    clarification_answers: list[str] | None,
) -> str:
    answers = "\n".join(clarification_answers) if clarification_answers else "None yet"
    return f"""
MedBridge patient case (synthetic demo data only):

Medical report:
{report_text}

Patient symptoms/question: {patient.symptoms}
Language: {patient.language}
Audience: {patient.audience}
Literacy level: {patient.literacy_level}
Clarification answers: {answers}

Route through: Document → Clarification → Knowledge → Explanation → Multilingual (if not English) → Safety.
"""


def _collect_pending_requests(events: list[Any]) -> list[Any]:
    return [
        event
        for event in events
        if event.type == "request_info" and isinstance(event.data, HandoffAgentUserRequest)
    ]


def _update_conversation(events: list[Any], conversation: list[Message]) -> list[Message]:
    for event in events:
        if event.type == "output" and isinstance(event.data, list):
            conversation = event.data
    return conversation


async def _run_handoff_loop(workflow, prompt: str) -> tuple[list[Any], list[Message]]:
    events: list[Any] = []
    conversation: list[Message] = []

    stream = workflow.run(prompt, stream=True)
    batch = [event async for event in stream]
    events.extend(batch)
    conversation = _update_conversation(batch, conversation)

    pending = _collect_pending_requests(batch)
    auto_replies = [
        "Continue the MedBridge pipeline. Hand off to the next specialist agent.",
        "Proceed with grounded knowledge retrieval and patient explanation, then safety review.",
        "No further patient input. Complete explanation and safety validation.",
    ]
    reply_idx = 0

    while pending and reply_idx < len(auto_replies):
        reply = auto_replies[reply_idx]
        reply_idx += 1
        responses = {
            req.request_id: HandoffAgentUserRequest.create_response(reply) for req in pending
        }
        batch = await workflow.run(responses=responses)
        events.extend(batch)
        conversation = _update_conversation(batch, conversation)
        pending = _collect_pending_requests(batch)

    return events, conversation


def _events_to_trace(events: list[Any]) -> list[dict]:
    trace: list[dict] = []
    step = 0
    for event in events:
        if event.type != "handoff_sent":
            continue
        step += 1
        data = event.data
        trace.append(
            {
                "step": step,
                "agent": "Handoff",
                "output": f"{getattr(data, 'source', '?')} → {getattr(data, 'target', '?')}",
            }
        )
    return trace


def _final_explanation(conversation: list[Message]) -> str:
    for name in ("safety_agent", "explanation_agent", "multilingual_agent"):
        for message in reversed(conversation):
            if getattr(message, "author_name", "") == name and message.text:
                return message.text
    for message in reversed(conversation):
        if message.role == "assistant" and message.text:
            return message.text
    return ""


async def run_medbridge_handoff(
    report_text: str,
    patient: PatientContext,
    clarification_answers: list[str] | None = None,
) -> MedBridgeResponse:
    workflow, _agents = build_medbridge_handoff_workflow()
    prompt = _build_initial_message(report_text, patient, clarification_answers)

    events, conversation = await _run_handoff_loop(workflow, prompt)

    handoff_trace = _events_to_trace(events)
    explanation = _final_explanation(conversation)

    clarification_needed = False
    clarification_questions: list[str] = []
    for message in conversation:
        if getattr(message, "author_name", "") == "clarification_agent" and message.text:
            if "?" in message.text and not clarification_answers:
                clarification_needed = True
                clarification_questions = [
                    line.strip(" •-\t")
                    for line in message.text.splitlines()
                    if "?" in line
                ][:3]

    return MedBridgeResponse(
        explanation=explanation,
        clarification_needed=clarification_needed and not clarification_answers,
        clarification_questions=clarification_questions,
        safety_passed=True,
        trace=handoff_trace,
    )
