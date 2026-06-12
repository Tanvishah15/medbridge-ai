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

## Agent prompts summary (Step 261)

Canonical prompt text lives in [`agents/prompts.py`](../agents/prompts.py). Orchestrator helpers add their own instructions in `orchestrator/planner.py` and `orchestrator/reflection.py`.

### Document Intelligence

**Goal:** Extract only what the report states — never diagnose.

| Key rule | Detail |
|----------|--------|
| Output | JSON: `diagnosis`, `findings[]`, `affected_area`, `recommendations[]` |
| Constraint | Never diagnose; extract report text only |
| Fallback | Empty/malformed input → empty fields + helpful finding message |

### Workflow Planner

**Goal:** Decide clarification, knowledge queries, and multilingual routing before agents run.

| Key rule | Detail |
|----------|--------|
| Output | JSON: `needs_clarification`, `knowledge_queries[]`, `use_multilingual`, `rationale` |
| Clarification | `true` when symptoms lack duration, pain, or fever and no answers yet |
| Knowledge | 1–3 focused queries combining symptoms + report diagnosis |
| Language | `use_multilingual=true` when target language ≠ English |

### Clarification

**Goal:** Ask what's missing — do not explain yet.

| Key rule | Detail |
|----------|--------|
| Questions | 1–3 short questions in the **patient's language** |
| Topics | Fever, pain level, duration, worsening symptoms |
| Skip | Return `[]` when symptoms already complete |
| Limit | Never more than 3 questions |

### Medical Knowledge

**Goal:** Grounded facts from Foundry IQ only.

| Key rule | Detail |
|----------|--------|
| Tool | Must call `knowledge_base_retrieve` before answering |
| Citations | End with `【source: document_name】` markers |
| Safety | Never invent drugs, dosages, or facts not in retrieval |
| Empty KB | Say grounded information was not found |

### Patient Explanation

**Goal:** Empathetic plain-language summary tied to the **report**, not vague wellness chat.

| Key rule | Detail |
|----------|--------|
| Priority | Report findings first; connect symptoms to report when possible |
| Phrasing | *"Your report shows…"* — never *"You have [condition]"* |
| Literacy | `simple` = short sentences; `standard` = more detail |
| Audience | `family` = warm grandmother-friendly tone and analogies |
| Anatomy | Correct terms (middle ear, not temple) |
| Language | **English only** — Multilingual agent translates later |
| Treatment | *"Follow your doctor's plan"* — no new prescriptions |

### Multilingual

**Goal:** Translate and culturally adapt — preserve medical accuracy.

| Key rule | Detail |
|----------|--------|
| Languages | Hindi, Spanish, Arabic, etc. |
| Family mode | Warmer, simpler tone for elderly relatives |
| Anatomy | Correct target-language terms (e.g. Hindi middle ear ≠ temple) |
| Disclaimer | Required in **target language** — educational only, consult doctor |

### Self-Reflection

**Goal:** Catch ungrounded explanations before safety review.

| Key rule | Detail |
|----------|--------|
| Output | JSON: `grounded`, `confidence`, `missing_topics`, `follow_up_query` |
| Low confidence | Invented facts, ignored report findings, weak symptom link |
| Retry | Optional `follow_up_query` triggers knowledge re-retrieval |

### Safety

**Goal:** Primary output guardrail — block unsafe medical advice.

| Block | Allow |
|-------|-------|
| Direct diagnosis (*"you have X"*) without report framing | *"Your report shows…"* |
| New prescriptions with drug names / dosages | Conditions named **from the report** with report framing |
| Stop-treatment advice | Paraphrase report follow-up / doctor's plan |
| Dismissing emergencies | *"As prescribed by your doctor"* |
| — | Add *consult your doctor* if disclaimer missing |
| — | Emergency symptoms → advise urgent care immediately |

Rule-based checks in `agents/safety_agent.py` run **before** LLM review for fast paths; LLM fallback when flags are ambiguous.

### Non-LLM guardrails

| Layer | File | Prompt? |
|-------|------|---------|
| Input PII block | `agents/input_guardrails.py` | Regex rules (SSN, card, email) |
| Output PII redact | `agents/output_guardrails.py` | Redaction + disclaimer enforcement |

### Handoff workflow variant

`orchestrator/handoff_workflow.py` reuses the same six agent prompts plus a **Triage** instruction for HandoffBuilder routing. Production UI uses the sequential orchestrator in `orchestrator/workflow.py`.

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

Optional OpenTelemetry tracing via Agent Framework. Off by default; enable with `MEDBRIDGE_ENABLE_OTEL=true`. See [observability.md](observability.md) and [foundry_tracing_setup.md](foundry_tracing_setup.md) (Step 237 portal).
