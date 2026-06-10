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


setup_logging()
