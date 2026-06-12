import os

from dotenv import load_dotenv

load_dotenv()

_SECRET_KEYS = (
    "AZURE_AI_PROJECT_ENDPOINT",
    "AZURE_AI_MODEL_DEPLOYMENT",
    "AZURE_AI_MODEL_DEPLOYMENT_FAST",
    "FOUNDRY_IQ_KB_NAME",
    "AZURE_SEARCH_ENDPOINT",
    "FOUNDRY_MCP_CONNECTION_NAME",
    "AZURE_TENANT_ID",
    "AZURE_CLIENT_ID",
    "AZURE_CLIENT_SECRET",
    "MEDBRIDGE_WORKFLOW_TIMEOUT_SECONDS",
    "MEDBRIDGE_MAX_CLARIFICATION_ROUNDS",
)


def _get_secret(name: str, default: str = "") -> str:
    """Read from os.environ first, then Streamlit Cloud secrets."""
    env_val = os.environ.get(name, "").strip().strip('"').strip("'")
    if env_val:
        return env_val
    try:
        import streamlit as st

        if name in st.secrets:
            val = str(st.secrets[name]).strip().strip('"').strip("'")
            if val:
                os.environ[name] = val
                return val
    except Exception:
        pass
    return default


def _merge_streamlit_secrets() -> None:
    """Load Streamlit Cloud secrets into os.environ."""
    try:
        import streamlit as st

        for key in st.secrets:
            value = st.secrets[key]
            if isinstance(value, (str, int, float, bool)):
                os.environ[str(key)] = str(value)
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    env_key = f"{str(key).upper()}_{str(sub_key).upper()}"
                    os.environ[env_key] = str(sub_value)
    except Exception:
        pass


def _apply_config_from_env() -> None:
    global PROJECT_ENDPOINT, MODEL_DEPLOYMENT, MODEL_DEPLOYMENT_FAST
    global KNOWLEDGE_BASE_NAME, AZURE_SEARCH_ENDPOINT, MCP_CONNECTION_NAME
    global WORKFLOW_TIMEOUT_SECONDS, MAX_CLARIFICATION_ROUNDS

    PROJECT_ENDPOINT = _get_secret("AZURE_AI_PROJECT_ENDPOINT")
    MODEL_DEPLOYMENT = _get_secret("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4o")
    MODEL_DEPLOYMENT_FAST = _get_secret("AZURE_AI_MODEL_DEPLOYMENT_FAST", MODEL_DEPLOYMENT)
    KNOWLEDGE_BASE_NAME = _get_secret("FOUNDRY_IQ_KB_NAME", "medbridge-medical-kb")
    AZURE_SEARCH_ENDPOINT = _get_secret("AZURE_SEARCH_ENDPOINT")
    MCP_CONNECTION_NAME = _get_secret("FOUNDRY_MCP_CONNECTION_NAME", "medbridge-kb-mcp-connection")
    WORKFLOW_TIMEOUT_SECONDS = int(_get_secret("MEDBRIDGE_WORKFLOW_TIMEOUT_SECONDS", "300"))
    MAX_CLARIFICATION_ROUNDS = int(_get_secret("MEDBRIDGE_MAX_CLARIFICATION_ROUNDS", "2"))


def bootstrap_environment() -> None:
    load_dotenv()
    _merge_streamlit_secrets()
    _apply_config_from_env()


bootstrap_environment()

PROJECT_ENDPOINT = _get_secret("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = _get_secret("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4o")
MODEL_DEPLOYMENT_FAST = _get_secret("AZURE_AI_MODEL_DEPLOYMENT_FAST", MODEL_DEPLOYMENT)
KNOWLEDGE_BASE_NAME = _get_secret("FOUNDRY_IQ_KB_NAME", "medbridge-medical-kb")
AZURE_SEARCH_ENDPOINT = _get_secret("AZURE_SEARCH_ENDPOINT")
MCP_CONNECTION_NAME = _get_secret("FOUNDRY_MCP_CONNECTION_NAME", "medbridge-kb-mcp-connection")
WORKFLOW_TIMEOUT_SECONDS = int(_get_secret("MEDBRIDGE_WORKFLOW_TIMEOUT_SECONDS", "300"))
MAX_CLARIFICATION_ROUNDS = int(_get_secret("MEDBRIDGE_MAX_CLARIFICATION_ROUNDS", "2"))


def azure_configured() -> bool:
    bootstrap_environment()
    return bool(_get_secret("AZURE_AI_PROJECT_ENDPOINT"))


def azure_cloud_credentials_configured() -> bool:
    bootstrap_environment()
    return all(_get_secret(key) for key in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET"))


def is_streamlit_cloud() -> bool:
    """True on Streamlit Community Cloud (/mount/src workspace)."""
    return os.path.isdir("/mount/src")
