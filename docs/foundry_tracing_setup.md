# Step 237 — Foundry portal tracing setup

Enable and view MedBridge agent traces in **Azure AI Foundry → Observability → Traces**.

References:
- [Set up tracing in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-setup)
- [Configure tracing for agent frameworks](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-framework)
- [Client-side tracing](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-client-side)

MedBridge runs **outside** Foundry (Streamlit / local Python), so you use **client-side** OpenTelemetry export to the Application Insights resource linked to your project.

---

## Part A — Portal (one-time)

### 1. Open your Foundry project

1. Go to [Microsoft Foundry](https://ai.azure.com)
2. Open project: **medbridge-ai-project-us** (or your project name)
3. Note the **Project endpoint** on Overview (matches `AZURE_AI_PROJECT_ENDPOINT` in `.env`)

### 2. Connect Application Insights

1. In the project, go to **Management** → **Connected resources** (or **Observability** setup)
2. Under **Application Insights**, click **Connect** if not already linked
3. Create a new App Insights resource or select an existing one in the same subscription
4. Save — tracing storage is now enabled for the project

### 3. Copy the connection string

1. Open the linked **Application Insights** resource in Azure Portal
2. Go to **Overview** → **Properties** → **Connection string**
3. Copy the full connection string

Or from Azure CLI:

```powershell
az monitor app-insights component show `
  --app <your-app-insights-name> `
  --resource-group medbridge-rg `
  --query connectionString -o tsv
```

### 4. IAM (if traces don’t show)

Your account needs **Log Analytics Reader** (or Monitoring Reader) on the Application Insights / Log Analytics workspace.

---

## Part B — Local export to Foundry

Add to `.env` (do **not** commit this value):

```env
MEDBRIDGE_ENABLE_OTEL=true
OTEL_SERVICE_NAME=medbridge-ai
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...;IngestionEndpoint=...
```

Optional — local console spans while testing:

```env
MEDBRIDGE_OTEL_CONSOLE=true
```

Install Azure Monitor exporter (one-time):

```powershell
.venv\Scripts\Activate.ps1
pip install azure-monitor-opentelemetry
```

Generate traffic:

```powershell
python tests/run_eval.py --case eval_001
# or
streamlit run ui/app.py
```

---

## Part C — View traces in Foundry portal

1. Wait **2–5 minutes** after a workflow run (ingestion delay is normal)
2. Foundry project → **Observability** → **Traces**
3. You should see traces with:
   - `medbridge.workflow`
   - `medbridge.agent.run`
   - `invoke_agent DocumentIntelligenceAgent`, `ClarificationAgent`, etc.
   - Token usage and latency on `chat gpt-4.1-mini` spans

### Filter tips

- Sort by **time** (most recent first)
- Look for `service.name = medbridge-ai`
- Open a trace → expand spans to show the agent pipeline for judges

### Screenshot for submission (optional)

Capture **Observability → Traces** with one MedBridge run visible — good bonus point vs competitors.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No traces in portal | Confirm App Insights is connected to Foundry project |
| Still empty after 5 min | Re-run eval; verify `APPLICATIONINSIGHTS_CONNECTION_STRING` in `.env` |
| Import error | `pip install azure-monitor-opentelemetry` |
| Permission denied | Add Log Analytics Reader on App Insights |
| Console works, portal empty | Connection string missing or wrong resource |

---

## What you already verified (Step 236)

Local console test showed:

```
medbridge.workflow
  ├── medbridge.agent.run (DocumentIntelligenceAgent)
  ├── medbridge.agent.run (WorkflowPlanner)
  └── medbridge.agent.run (ClarificationAgent)
```

Step 237 sends the same spans to Azure so judges can see them in the **Foundry portal UI**.
