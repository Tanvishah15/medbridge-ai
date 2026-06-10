import asyncio
import os
import sys

from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()

async def main():
    try:
        from agent_framework.foundry import FoundryChatClient
    except ImportError:
        print("Run: pip install agent-framework")
        sys.exit(1)

    project_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4.1-mini")

    if not project_endpoint:
        print("Missing AZURE_AI_PROJECT_ENDPOINT in .env")
        sys.exit(1)

    client = FoundryChatClient(
        project_endpoint=project_endpoint,
        model=model,
        credential=AzureCliCredential(),
    )
    agent = client.as_agent(
        name="TestAgent",
        instructions="You are a helpful assistant. Reply in one sentence.",
    )
    result = await agent.run("Say hello")
    print("Model response:", result.text)

if __name__ == "__main__":
    asyncio.run(main())
