from typing import Any

from agents.logging_config import preview


class ReasoningTrace:
    """Step-by-step reasoning log for judges and demo UI."""

    def __init__(self) -> None:
        self._steps: list[dict[str, Any]] = []

    def add(self, agent: str, output: Any) -> None:
        self._steps.append(
            {
                "step": len(self._steps) + 1,
                "agent": agent,
                "output": preview(output),
            }
        )

    def to_list(self) -> list[dict[str, Any]]:
        return list(self._steps)
