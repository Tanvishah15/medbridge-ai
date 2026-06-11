import asyncio
import logging
import os

from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential, ClientSecretCredential, DefaultAzureCredential

import config

from agents import logging_config  # noqa: F401

logger = logging.getLogger(__name__)

AGENT_TIMEOUT_SECONDS = 30
AGENT_MAX_RETRIES = 1


def get_azure_credential():
    """Local dev: Azure CLI. Streamlit Cloud: service principal env vars."""
    tenant_id = os.environ.get("AZURE_TENANT_ID", "").strip()
    client_id = os.environ.get("AZURE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("AZURE_CLIENT_SECRET", "").strip()
    if tenant_id and client_id and client_secret:
        return ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )

    try:
        return AzureCliCredential()
    except Exception:
        return DefaultAzureCredential()


def get_chat_client(fast: bool = False) -> FoundryChatClient:
    config.bootstrap_environment()
    model = config.MODEL_DEPLOYMENT_FAST if fast else config.MODEL_DEPLOYMENT
    endpoint = config.PROJECT_ENDPOINT
    return FoundryChatClient(
        project_endpoint=endpoint,
        model=model,
        credential=get_azure_credential(),
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
