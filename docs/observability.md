# Step 236 — OpenTelemetry tracing (bonus)

MedBridge uses [Microsoft Agent Framework observability](https://learn.microsoft.com/en-us/agent-framework/agents/observability) for GenAI traces, logs, and metrics.

## Enable locally

Add to `.env`:

```env
MEDBRIDGE_ENABLE_OTEL=true
MEDBRIDGE_OTEL_CONSOLE=true
OTEL_SERVICE_NAME=medbridge-ai
```

Run the app or eval:

```powershell
.venv\Scripts\Activate.ps1
streamlit run ui/app.py
# or
python tests/run_eval.py --case eval_001
```

Console output shows OpenTelemetry spans for:

- `medbridge.workflow` — full orchestrator run
- `medbridge.agent.run` — each LLM agent call
- Agent Framework auto-spans — model calls, MCP/Foundry IQ tool use

## Export to Azure Monitor / Foundry (Step 237)

Set standard OTLP variables instead of console:

```env
MEDBRIDGE_ENABLE_OTEL=true
OTEL_EXPORTER_OTLP_ENDPOINT=https://<your-monitor-endpoint>
OTEL_SERVICE_NAME=medbridge-ai
```

Then review traces in **Azure AI Foundry → your project → Tracing**.

## Implementation

| File | Role |
|------|------|
| `orchestrator/telemetry.py` | `setup_observability()`, span helpers |
| `config.py` | Calls setup during `bootstrap_environment()` |
| `orchestrator/workflow.py` | `@trace_async_workflow` on `run_medbridge` |
| `agents/base.py` | Span around `run_agent()` |

Tracing is **off by default** so Streamlit Cloud and tests stay quiet unless you opt in.
