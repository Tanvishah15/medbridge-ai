import os

from dotenv import load_dotenv

load_dotenv()


def _merge_streamlit_secrets() -> None:
    """Load Streamlit Cloud secrets into os.environ before config is read."""
    try:
        import streamlit as st

        for key, value in st.secrets.items():
            if isinstance(value, (str, int, float, bool)):
                os.environ.setdefault(str(key), str(value))
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    env_key = f"{str(key).upper()}_{str(sub_key).upper()}"
                    os.environ.setdefault(env_key, str(sub_value))
    except Exception:
        pass


def bootstrap_environment() -> None:
    load_dotenv()
    _merge_streamlit_secrets()


bootstrap_environment()

PROJECT_ENDPOINT = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
MODEL_DEPLOYMENT = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4o")
MODEL_DEPLOYMENT_FAST = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_FAST", MODEL_DEPLOYMENT)
KNOWLEDGE_BASE_NAME = os.environ.get("FOUNDRY_IQ_KB_NAME", "medbridge-medical-kb")
AZURE_SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
MCP_CONNECTION_NAME = os.environ.get("FOUNDRY_MCP_CONNECTION_NAME", "medbridge-kb-mcp-connection")

WORKFLOW_TIMEOUT_SECONDS = int(os.environ.get("MEDBRIDGE_WORKFLOW_TIMEOUT_SECONDS", "300"))
MAX_CLARIFICATION_ROUNDS = int(os.environ.get("MEDBRIDGE_MAX_CLARIFICATION_ROUNDS", "2"))


def azure_configured() -> bool:
    return bool(PROJECT_ENDPOINT.strip())


def azure_cloud_credentials_configured() -> bool:
    return all(
        os.environ.get(key, "").strip()
        for key in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET")
    )
