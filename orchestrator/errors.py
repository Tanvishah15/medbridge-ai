import asyncio


def friendly_error_message(exc: Exception) -> str:
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

    return (
        "Something went wrong while analyzing your report. "
        "Please try again, or use one of the demo reports. "
        "This is a demo only — not medical advice."
    )
