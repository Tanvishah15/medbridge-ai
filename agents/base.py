from azure.identity import AzureCliCredential
from agent_framework.foundry import FoundryChatClient
from config import PROJECT_ENDPOINT, MODEL_DEPLOYMENT


def get_chat_client() -> FoundryChatClient:
    return FoundryChatClient(
        project_endpoint=PROJECT_ENDPOINT,
        model=MODEL_DEPLOYMENT,
        credential=AzureCliCredential(),
    )
