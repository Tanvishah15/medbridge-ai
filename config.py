import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ENDPOINT = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4o")
MODEL_DEPLOYMENT_FAST = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_FAST", MODEL_DEPLOYMENT)
KNOWLEDGE_BASE_NAME = os.environ.get("FOUNDRY_IQ_KB_NAME", "medbridge-medical-kb")
AZURE_SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
MCP_CONNECTION_NAME = os.environ.get("FOUNDRY_MCP_CONNECTION_NAME", "medbridge-kb-mcp-connection")

# Step 201 — total workflow timeout (per-agent timeout remains 30s in agents/base.py)
WORKFLOW_TIMEOUT_SECONDS = int(os.environ.get("MEDBRIDGE_WORKFLOW_TIMEOUT_SECONDS", "300"))

# Step 206 — max clarification rounds before auto-continuing
MAX_CLARIFICATION_ROUNDS = int(os.environ.get("MEDBRIDGE_MAX_CLARIFICATION_ROUNDS", "2"))
