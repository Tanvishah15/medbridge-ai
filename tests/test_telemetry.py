"""Step 236 — OpenTelemetry bootstrap tests (no live export)."""

import orchestrator.telemetry as telemetry


def test_observability_disabled_by_default(monkeypatch):
    monkeypatch.delenv("MEDBRIDGE_ENABLE_OTEL", raising=False)
    monkeypatch.delenv("ENABLE_INSTRUMENTATION", raising=False)
    assert telemetry.observability_enabled() is False
    assert telemetry.setup_observability() is False


def test_observability_enabled_flag(monkeypatch):
    monkeypatch.setenv("MEDBRIDGE_ENABLE_OTEL", "true")
    assert telemetry.observability_enabled() is True


def test_workflow_span_noop_when_not_configured():
    with telemetry.workflow_span("test.span", language="Hindi"):
        assert telemetry.is_configured() is False


def test_falls_back_when_azure_monitor_unavailable(monkeypatch):
    monkeypatch.setenv("MEDBRIDGE_ENABLE_OTEL", "true")
    monkeypatch.setenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "InstrumentationKey=test")
    monkeypatch.setattr(telemetry, "_setup_azure_monitor_export", lambda: False)
    telemetry._CONFIGURED = False
    assert telemetry.setup_observability() is True
    telemetry._CONFIGURED = False


def test_agent_display_name():
    class FakeAgent:
        name = "ClarificationAgent"

    assert telemetry.agent_display_name(FakeAgent()) == "ClarificationAgent"


def test_app_insights_connection_string_helper(monkeypatch):
    monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)
    assert telemetry._app_insights_connection_string() == ""
    monkeypatch.setenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "InstrumentationKey=abc")
    assert "InstrumentationKey=abc" in telemetry._app_insights_connection_string()
