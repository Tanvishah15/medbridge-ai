"""Create RemoteTool MCP connection for Foundry IQ (Step 112)."""

import requests
from azure.identity import AzureCliCredential, get_bearer_token_provider

PROJECT_RESOURCE_ID = (
    "/subscriptions/4bf058a3-65a4-4f05-8bb2-06abb02047f5"
    "/resourceGroups/rg-tjshah45-8825"
    "/providers/Microsoft.CognitiveServices/accounts/medbridge-ai-project-us-resource"
    "/projects/medbridge-ai-project-us"
)
CONNECTION_NAME = "medbridge-kb-mcp-connection"
MCP_ENDPOINT = (
    "https://medbridgesearchtj.search.windows.net"
    "/knowledgebases/medbridge-medical-kb/mcp?api-version=2026-05-01-preview"
)


def main() -> None:
    credential = AzureCliCredential()
    token = get_bearer_token_provider(credential, "https://management.azure.com/.default")()

    url = (
        f"https://management.azure.com{PROJECT_RESOURCE_ID}"
        f"/connections/{CONNECTION_NAME}?api-version=2025-10-01-preview"
    )
    payload = {
        "name": CONNECTION_NAME,
        "type": "Microsoft.MachineLearningServices/workspaces/connections",
        "properties": {
            "authType": "ProjectManagedIdentity",
            "category": "RemoteTool",
            "target": MCP_ENDPOINT,
            "isSharedToAll": True,
            "audience": "https://search.azure.com/",
            "metadata": {"ApiType": "Azure"},
        },
    }

    response = requests.put(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    print(f"SUCCESS: Connection '{CONNECTION_NAME}' created.")
    print(f"MCP endpoint: {MCP_ENDPOINT}")


if __name__ == "__main__":
    main()
