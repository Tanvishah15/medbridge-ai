# MedBridge AI — Architecture

## Agent Pipeline

```
User Upload + Message
        ↓
[Orchestrator]
        ↓
[Document Intelligence Agent] → structured report
        ↓
[Clarification Agent] → missing info? → ask questions → loop
        ↓
[Medical Knowledge Agent + Foundry IQ] → grounded facts + citations
        ↓
[Patient Explanation Agent] → simple language
        ↓
[Multilingual Agent] → target language
        ↓
[Safety Agent] → validate → final response
```

## Agent Roles (Steps 151–180)

| Agent | File | Role | Model | Timeout / Retry |
|-------|------|------|-------|-----------------|
| Document Intelligence | `agents/document_agent.py` | Parses blood, MRI, ENT, and other reports into structured JSON (`diagnosis`, `findings`, `affected_area`, `recommendations`). Handles empty/malformed input without crashing. | Primary (`AZURE_AI_MODEL_DEPLOYMENT`) | 30s / 1 retry |
| Medical Knowledge | `agents/knowledge_agent.py` | Retrieves grounded facts via Foundry IQ MCP (`knowledge_base_retrieve`). Always requests citations. Flags ungrounded drug names. | Primary | 30s / 1 retry |
| Clarification | `agents/clarification_agent.py` | Asks 0–3 questions in patient language when symptoms lack duration, pain, or fever info. Skips when symptoms are complete. | Fast (`AZURE_AI_MODEL_DEPLOYMENT_FAST`) | 30s / 1 retry |
| Patient Explanation | `agents/explanation_agent.py` | Converts findings into empathetic patient language. Supports `simple` and `standard` literacy modes. | Primary | 30s / 1 retry |
| Multilingual | `agents/multilingual_agent.py` | Translates for Hindi, Spanish, Arabic, etc. Family audience uses warmer tone. Always includes disclaimer. | Fast | 30s / 1 retry |
| Safety | `agents/safety_agent.py` | Blocks diagnosis, prescriptions, treatment changes. Escalates emergencies. Safe responses pass through unchanged. | Primary | 30s / 1 retry |

## Reliability

All agents call `run_agent()` in `agents/base.py`:
- **30-second timeout** per LLM call (Step 171)
- **1 retry** on timeout or transient failure (Step 172)
- Structured **INPUT/OUTPUT logging** via `agents/logging_config.py` (Steps 148–149)

## Model Strategy (Step 175)

| Tier | Env Variable | Used By |
|------|--------------|---------|
| Primary | `AZURE_AI_MODEL_DEPLOYMENT` | Document, Knowledge, Explanation, Safety |
| Fast | `AZURE_AI_MODEL_DEPLOYMENT_FAST` | Clarification, Multilingual (defaults to primary if unset) |

Run `python scripts/profile_agents.py` to identify the slowest agent (Step 174).

## Components

| Folder | Purpose |
|--------|---------|
| `agents/` | Six specialized reasoning agents + shared utils |
| `orchestrator/` | Sequential + handoff workflow |
| `knowledge/` | Foundry IQ setup documentation |
| `data/` | Synthetic reports and knowledge docs |
| `ui/` | Streamlit patient-facing app |
| `tests/` | Unit, refinement, and integration tests |
| `scripts/` | Auth, profiling, and connectivity scripts |

## Tech Stack

- Python 3.12
- Microsoft Agent Framework + Foundry
- Foundry IQ (Azure AI Search + Blob Storage)
- Streamlit

## Testing (Steps 178–179)

```powershell
pytest tests/ -v
python scripts/profile_agents.py
```

See [sample_outputs.md](sample_outputs.md) for demo output examples (Step 177).

## Evaluation (Steps 232–235)

MedBridge is judged on five criteria: **grounding**, **safety**, **multilingual output**, **clarification loop**, and **symptom-to-report matching**.

See [evaluation_criteria.md](evaluation_criteria.md) for pass/fail definitions and scoring rubric.

## Observability (Steps 236–237)

Optional OpenTelemetry tracing via Agent Framework. Off by default; enable with `MEDBRIDGE_ENABLE_OTEL=true`. See [observability.md](observability.md).
