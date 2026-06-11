import json
import logging
from typing import Any

LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
PREVIEW_MAX_LEN = 200


def setup_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=level, format=LOG_FORMAT)


def preview(value: Any, max_len: int = PREVIEW_MAX_LEN) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, default=str)
    else:
        text = str(value)
    text = " ".join(text.split())
    if len(text) <= max_len:
        return text
    return f"{text[: max_len - 3]}..."


def log_agent_input(agent: str, **fields: Any) -> None:
    log = logging.getLogger("medbridge.agents")
    for key, value in fields.items():
        log.info("%s | INPUT | %s=%s", agent, key, preview(value))


def log_agent_output(agent: str, **fields: Any) -> None:
    log = logging.getLogger("medbridge.agents")
    for key, value in fields.items():
        log.info("%s | OUTPUT | %s=%s", agent, key, preview(value))


def estimate_tokens(*texts: str) -> int:
    """Rough token estimate for cost tracking (Step 207)."""
    total_chars = sum(len(text or "") for text in texts)
    return max(1, total_chars // 4)


def log_workflow_metrics(
    workflow: str,
    *,
    duration_seconds: float,
    trace_steps: int,
    report_chars: int,
    explanation_chars: int,
    estimated_tokens: int,
) -> None:
    log = logging.getLogger("medbridge.metrics")
    log.info(
        "%s | METRICS | duration_s=%.2f trace_steps=%d report_chars=%d "
        "explanation_chars=%d estimated_tokens=%d",
        workflow,
        duration_seconds,
        trace_steps,
        report_chars,
        explanation_chars,
        estimated_tokens,
    )


setup_logging()
