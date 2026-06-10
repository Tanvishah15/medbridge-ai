import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ENDPOINT = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4o")
KNOWLEDGE_BASE_NAME = os.environ.get("FOUNDRY_IQ_KB_NAME", "medbridge-medical-kb")
AZURE_SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
MCP_CONNECTION_NAME = os.environ.get("FOUNDRY_MCP_CONNECTION_NAME", "medbridge-kb-mcp-connection")
