import asyncio

from agents.input_guardrails import InputGuardrailError


def friendly_error_message(exc: Exception) -> str:
    if isinstance(exc, InputGuardrailError):
        detail = "; ".join(exc.reasons)
        return (
            "Please use synthetic demo data only — do not paste real personal information "
            f"(SSN, credit card, or email). Detected: {detail}"
        )

    if isinstance(exc, ValueError):
        msg = str(exc)
        lower = msg.lower()
        if "checkpoint not found" in lower or "session checkpoint" in lower:
            return (
                "Your clarification session expired or was not found. "
                "Please start again with Understand My Report."
            )
        if "extract text" in lower or "uploaded pdf" in lower:
            return (
                "We could not read text from that PDF. "
                "Try a TXT demo report or paste the report text instead."
            )
        if "provide report" in lower:
            return "Please paste or upload a synthetic demo report."
        return msg

    if isinstance(exc, asyncio.TimeoutError):
        return (
            "MedBridge timed out while processing your request. "
            "Please try again with a shorter report."
        )

    lower = str(exc).lower()
    if "aadsts7000215" in lower or "invalid client secret" in lower:
        return (
            "Azure authentication failed: invalid client secret. "
            "In Streamlit Secrets, paste the secret VALUE (not the Secret ID) "
            "for AZURE_CLIENT_SECRET, then reboot the app."
        )
    if "authentication failed" in lower or "unauthorized" in lower:
        return (
            "Azure authentication failed on Streamlit Cloud. "
            "Check AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET in Secrets."
        )

    return (
        "Something went wrong while analyzing your report. "
        "Please try again, or use one of the demo reports. "
        "This is a demo only — not medical advice."
    )
