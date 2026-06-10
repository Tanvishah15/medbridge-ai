import asyncio
import logging

from azure.identity import AzureCliCredential
from agent_framework.foundry import FoundryChatClient
from config import MODEL_DEPLOYMENT, MODEL_DEPLOYMENT_FAST, PROJECT_ENDPOINT

from agents import logging_config  # noqa: F401

logger = logging.getLogger(__name__)

AGENT_TIMEOUT_SECONDS = 30
AGENT_MAX_RETRIES = 1


def get_chat_client(fast: bool = False) -> FoundryChatClient:
    model = MODEL_DEPLOYMENT_FAST if fast else MODEL_DEPLOYMENT
    return FoundryChatClient(
        project_endpoint=PROJECT_ENDPOINT,
        model=model,
        credential=AzureCliCredential(),
    )


async def run_agent(agent, prompt: str):
    last_error: Exception | None = None
    attempts = AGENT_MAX_RETRIES + 1

    for attempt in range(attempts):
        try:
            return await asyncio.wait_for(
                agent.run(prompt),
                timeout=AGENT_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError as exc:
            last_error = exc
            logger.warning(
                "Agent timed out after %ss (attempt %d/%d)",
                AGENT_TIMEOUT_SECONDS,
                attempt + 1,
                attempts,
            )
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Agent call failed (attempt %d/%d): %s",
                attempt + 1,
                attempts,
                exc,
            )

        if attempt == AGENT_MAX_RETRIES:
            break

    if last_error is not None:
        raise last_error
    raise RuntimeError("Agent call failed without an error")
