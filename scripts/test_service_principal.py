"""Test Azure service principal auth (for Streamlit Cloud debugging)."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

from azure.identity import ClientSecretCredential

TENANT = os.environ.get("AZURE_TENANT_ID", "").strip()
CLIENT = os.environ.get("AZURE_CLIENT_ID", "").strip()
SECRET = os.environ.get("AZURE_CLIENT_SECRET", "").strip().strip('"').strip("'")
ENDPOINT = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "").strip()


def main() -> int:
    print("=== Service Principal Auth Test ===")
    print(f"Tenant ID set: {bool(TENANT)}")
    print(f"Client ID set: {bool(CLIENT)}")
    print(f"Client secret length: {len(SECRET)} chars")
    print(f"Endpoint set: {bool(ENDPOINT)}")

    if not all([TENANT, CLIENT, SECRET]):
        print("\nFAIL: Missing AZURE_TENANT_ID, AZURE_CLIENT_ID, or AZURE_CLIENT_SECRET in .env")
        return 1

    if len(SECRET) < 20:
        print("\nFAIL: Secret looks too short — did you paste Secret ID instead of Value?")
        return 1

    try:
        cred = ClientSecretCredential(
            tenant_id=TENANT,
            client_id=CLIENT,
            client_secret=SECRET,
        )
        token = cred.get_token("https://cognitiveservices.azure.com/.default")
        print(f"\nOK: Got token (expires {token.expires_on})")
        print("Service principal works — use the SAME secret Value in Streamlit Secrets.")
        return 0
    except Exception as exc:
        print(f"\nFAIL: {exc}")
        print("\nFix: regenerate secret in Azure, copy VALUE column only, update .env + Streamlit Secrets.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
