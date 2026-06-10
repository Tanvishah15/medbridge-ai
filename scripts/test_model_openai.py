"""Simple model test using the same pattern as Foundry Playground."""
import os

from azure.identity import AzureCliCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4.1-mini")
resource_name = os.environ.get(
    "AZURE_FOUNDRY_RESOURCE",
    "medbridge-ai-project-us-resource",
)
endpoint = f"https://{resource_name}.services.ai.azure.com/openai/v1"

token_provider = get_bearer_token_provider(
    AzureCliCredential(),
    "https://ai.azure.com/.default",
)

client = OpenAI(base_url=endpoint, api_key=token_provider)

completion = client.chat.completions.create(
    model=deployment_name,
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
)

print("Model response:", completion.choices[0].message.content)
