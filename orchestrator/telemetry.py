"""Step 236 — OpenTelemetry tracing via Microsoft Agent Framework observability."""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

_CONFIGURED = False
F = TypeVar("F", bound=Callable[..., Any])


def observability_enabled() -> bool:
    """True when MEDBRIDGE_ENABLE_OTEL or ENABLE_INSTRUMENTATION is set."""
    for key in ("MEDBRIDGE_ENABLE_OTEL", "ENABLE_INSTRUMENTATION"):
        if os.environ.get(key, "").strip().lower() in ("1", "true", "yes"):
            return True
    return False


def console_exporters_enabled() -> bool:
    for key in ("MEDBRIDGE_OTEL_CONSOLE", "ENABLE_CONSOLE_EXPORTERS"):
        if os.environ.get(key, "").strip().lower() in ("1", "true", "yes"):
            return True
    return False


def setup_observability() -> bool:
    """Configure Agent Framework OpenTelemetry providers once at startup."""
    global _CONFIGURED
    if _CONFIGURED:
        return True
    if not observability_enabled():
        return False

    try:
        from agent_framework.observability import configure_otel_providers

        configure_otel_providers(
            enable_console_exporters=console_exporters_enabled(),
            enable_sensitive_data=False,
        )
        _CONFIGURED = True
        logger.info("OpenTelemetry enabled for MedBridge (Agent Framework GenAI conventions)")
        return True
    except Exception as exc:
        logger.warning("OpenTelemetry setup skipped: %s", exc)
        return False


def is_configured() -> bool:
    return _CONFIGURED


@contextmanager
def workflow_span(name: str, **attributes: Any) -> Iterator[None]:
    """Create a MedBridge workflow/agent span when OTel is active."""
    if not _CONFIGURED:
        yield
        return

    try:
        from agent_framework.observability import get_tracer
        from opentelemetry.trace import SpanKind, Status, StatusCode

        tracer = get_tracer()
        with tracer.start_as_current_span(name, kind=SpanKind.INTERNAL) as span:
            for key, value in attributes.items():
                if value is not None:
                    span.set_attribute(f"medbridge.{key}", str(value)[:500])
            try:
                yield
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise
    except Exception:
        yield


def trace_async_workflow(func: F) -> F:
    """Decorator for async workflow entrypoints."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        patient = kwargs.get("patient")
        if patient is None and len(args) > 1:
            patient = args[1]
        language = getattr(patient, "language", "")
        symptoms = getattr(patient, "symptoms", "")
        with workflow_span(
            "medbridge.workflow",
            language=language,
            symptoms_len=len(symptoms or ""),
        ):
            return await func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def agent_display_name(agent: Any) -> str:
    for attr in ("name", "id"):
        value = getattr(agent, attr, None)
        if value:
            return str(value)
    return type(agent).__name__
