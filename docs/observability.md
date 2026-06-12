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

Full portal guide: **[foundry_tracing_setup.md](foundry_tracing_setup.md)**

Quick steps:

1. Foundry project → connect **Application Insights**
2. Copy **connection string** into `.env`:
   ```env
   MEDBRIDGE_ENABLE_OTEL=true
   APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
   OTEL_SERVICE_NAME=medbridge-ai
   ```
3. `pip install azure-monitor-opentelemetry`
4. Run a workflow, wait 2–5 min
5. Foundry → **Observability → Traces**

For local debugging only (no portal), keep console export:

```env
MEDBRIDGE_OTEL_CONSOLE=true
```

## Implementation

| File | Role |
|------|------|
| `orchestrator/telemetry.py` | `setup_observability()`, span helpers |
| `config.py` | Calls setup during `bootstrap_environment()` |
| `orchestrator/workflow.py` | `@trace_async_workflow` on `run_medbridge` |
| `agents/base.py` | Span around `run_agent()` |

Tracing is **off by default** so Streamlit Cloud and tests stay quiet unless you opt in.
