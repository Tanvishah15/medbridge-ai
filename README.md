# MedBridge AI 🏥

> **"Don't just translate my medical report. Help me understand what's happening to me."**

Multilingual medical reasoning platform — six Foundry agents, clarification loop, Foundry IQ grounding, and layered safety guardrails.

![Tests](https://github.com/Tanvishah15/medbridge-ai/actions/workflows/test.yml/badge.svg)
**Live demo:** [medbridge-ai.streamlit.app](https://medbridge-ai.streamlit.app) · **Repo:** [github.com/Tanvishah15/medbridge-ai](https://github.com/Tanvishah15/medbridge-ai)

---

## Problem

Patients receive lab reports, imaging results, and discharge summaries they **cannot understand** — often in medical English while they speak Hindi, Spanish, or Arabic at home. Generic translators miss clinical context, skip symptom-to-report matching, and can sound like a doctor diagnosing or prescribing. Families need **grounded, safe, plain-language explanations** — not a wall of jargon.

## Solution

**MedBridge AI** is a multi-agent reasoning system on **Microsoft Foundry** that:

1. **Structures** uploaded synthetic reports (ENT, blood, MRI)
2. **Asks clarifying questions** when symptoms are incomplete (1–3 questions, max 2 rounds)
3. **Retrieves grounded facts** from **Foundry IQ** with citations
4. **Explains** in simple language matched to literacy and audience (patient vs family)
5. **Translates** to Hindi, Spanish, or Arabic with culturally appropriate tone
6. **Validates safety** — no diagnosis, prescription, or treatment-change advice

---

## Hackathon submission

| Field | Value |
|-------|--------|
| **Event** | Agents League Hackathon 2026 |
| **Track** | Reasoning Agents (Microsoft Foundry) |
| **IQ integration** | Foundry IQ — Azure AI Search knowledge base with citations |
| **Framework** | Microsoft Agent Framework (Python) |
| **UI** | Streamlit (live on Streamlit Cloud) |
| **Eval suite** | 10 automated cases — **100% pass** (see [Evaluation](#evaluation)) |

---

## Architecture

![MedBridge AI — multi-agent pipeline with Foundry IQ and safety guardrails](docs/screenshots/architecture-diagram.png)

*Diagram source:* [docs/architecture_diagram.mmd](docs/architecture_diagram.mmd) — regenerate with `npx @mermaid-js/mermaid-cli -i docs/architecture_diagram.mmd -o docs/screenshots/architecture-diagram.png`

```mermaid
flowchart TD
    U[User — Streamlit UI] --> IG[Input Guardrails]
    IG --> B[Orchestrator]
    B --> C[Document Intelligence Agent]
    C --> D[Clarification Agent]
    D -->|needs info| U
    D --> E[Medical Knowledge Agent + Foundry IQ]
    E --> F[Patient Explanation Agent]
    F --> G[Multilingual Agent]
    G --> H[Safety Agent]
    H --> OG[Output Guardrails]
    OG --> U
```

Full design: [docs/architecture.md](docs/architecture.md) · Observability: [docs/observability.md](docs/observability.md)

---

## Agents

| Agent | Role |
|-------|------|
| **Document Intelligence** | Parses synthetic reports into structured JSON |
| **Clarification** | Asks follow-up questions when symptoms are vague |
| **Medical Knowledge** | Foundry IQ retrieval with citations |
| **Patient Explanation** | Empathetic plain-language summary |
| **Multilingual** | Hindi, Spanish, Arabic (family/grandmother tone) |
| **Safety** | Blocks diagnosis / prescription / stop-medication advice |

All agents: 30s timeout, 1 retry, structured logging. See [docs/sample_outputs.md](docs/sample_outputs.md).

---

## Demo scenarios

| # | Persona | Language | Report | Wow moment |
|---|---------|----------|--------|------------|
| **1** | Hindi patient, ear discharge | Hindi | ENT otitis media | Clarification loop → symptom-to-report match in Hindi |
| **2** | Family explaining to grandmother | Spanish | Blood test / sugar | Warm family summary, not raw translation |
| **3** | Family MRI summary | Arabic | Brain MRI | Arabic script output with safe microvascular framing |

Script and judge talking points: [docs/demo_scenarios.md](docs/demo_scenarios.md)

### Screenshots

![Demo preset loaded — Hindi ENT](docs/screenshots/streamlit-ui-demo-loaded.png)

![Hindi explanation with safety badge and Foundry IQ sources](docs/screenshots/streamlit-ui-demo-ent.png)

![Agent reasoning trace](docs/screenshots/streamlit-ui-trace.png)

---

## Setup

### Prerequisites

- Python 3.12+
- Azure AI Foundry project with model deployment
- Foundry IQ knowledge base (optional for full grounding demo)
- Azure service principal for Streamlit Cloud

### 1. Clone and install

See [How to Run → One-time setup](#one-time-setup).

### 2. Configure environment

Copy keys from [.streamlit/secrets.toml.example](.streamlit/secrets.toml.example) into a local `.env` file (never commit):

```env
AZURE_AI_PROJECT_ENDPOINT=https://YOUR-PROJECT.services.ai.azure.com/api/projects/YOUR-PROJECT
AZURE_AI_MODEL_DEPLOYMENT=gpt-4.1-mini
AZURE_AI_MODEL_DEPLOYMENT_FAST=gpt-4.1-mini
FOUNDRY_IQ_KB_NAME=medbridge-medical-kb
AZURE_SEARCH_ENDPOINT=https://YOUR-SEARCH.search.windows.net
FOUNDRY_MCP_CONNECTION_NAME=medbridge-kb-mcp-connection
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

Streamlit Cloud: use [.streamlit/secrets.toml.example](.streamlit/secrets.toml.example) as a template in **Manage app → Secrets**.

---

## How to Run

All commands assume you are in the repo root (`medbridge-ai/`). On Windows use PowerShell.

### One-time setup

```powershell
git clone https://github.com/Tanvishah15/medbridge-ai.git
cd medbridge-ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` from [.streamlit/secrets.toml.example](.streamlit/secrets.toml.example) (see [Setup](#setup) above). **Never commit `.env`.**

### Verify Azure (optional)

```powershell
cd medbridge-ai
.\.venv\Scripts\Activate.ps1
python scripts/test_foundry.py
python scripts/test_service_principal.py
```

### Streamlit UI (primary demo)

```powershell
cd medbridge-ai
.\.venv\Scripts\Activate.ps1
streamlit run ui/app.py
```

Open **http://localhost:8501** → choose a demo preset (e.g. Hindi ENT) → click **Understand My Report**.

**Live (no install):** [medbridge-ai.streamlit.app](https://medbridge-ai.streamlit.app)

### CLI workflow smoke test

```powershell
cd medbridge-ai
.\.venv\Scripts\Activate.ps1
python -m orchestrator.workflow
```

Or: `python scripts/test_workflow.py`

### Automated eval suite

```powershell
cd medbridge-ai
.\.venv\Scripts\Activate.ps1
python tests/run_eval.py --output tests/eval_results_full.json
python tests/run_eval.py --parity
python tests/run_eval.py --case eval_008 --case eval_009 --case eval_010
python tests/run_eval.py --dry-run
```

Target: **≥ 80%** suite score (current: **100%** — 10/10 cases).

### Unit tests (no Azure)

```powershell
cd medbridge-ai
.\.venv\Scripts\Activate.ps1
pytest tests/ `
  --ignore=tests/test_workflow.py `
  --ignore=tests/test_demo_scenarios.py `
  --ignore=tests/test_handoff_workflow.py `
  --ignore=tests/test_agents.py `
  --ignore=tests/test_agent_refinement.py `
  --ignore=tests/test_workflow_hardening.py `
  -q
```

### Full integration tests (Azure required)

```powershell
cd medbridge-ai
.\.venv\Scripts\Activate.ps1
pytest tests/test_workflow.py tests/test_demo_scenarios.py -v
python scripts/test_demo_scenarios.py
python scripts/profile_agents.py
```

### macOS / Linux

```bash
cd medbridge-ai
source .venv/bin/activate
pip install -r requirements.txt
streamlit run ui/app.py
```

---

## Foundry IQ integration 🏆

MedBridge uses **Microsoft Foundry IQ** as the hackathon **IQ layer** — medical facts come from a indexed knowledge base, not from model memory alone. The **Medical Knowledge Agent** calls `knowledge_base_retrieve` via MCP and passes citations to the Explanation Agent.

### How it works in the pipeline

```
data/synthetic_knowledge/*.md  →  Azure Blob  →  Foundry IQ KB  →  MCP  →  Medical Knowledge Agent  →  citations in UI
```

1. **Upload** synthetic markdown docs to Azure Blob Storage  
2. **Index** them in a Foundry IQ knowledge base (Azure AI Search)  
3. **Connect** the KB to your Foundry project via **MCP** (`knowledge_base_retrieve`)  
4. At runtime, the orchestrator queries the KB with planner-generated questions  
5. Retrieved chunks appear as **citations** in the Streamlit UI and eval scoring  

### Knowledge base contents

All sources live in [`data/synthetic_knowledge/`](data/synthetic_knowledge/) (demo-only):

| Document | Purpose |
|----------|---------|
| `otitis_media.md` | ENT / middle ear condition explainer |
| `type2_diabetes.md` | Blood sugar / HbA1c context |
| `cholesterol.md` | LDL/HDL patient language |
| `microvascular_changes.md` | Brain MRI white-matter changes |
| `symptom_connections.md` | Links symptoms (e.g. ear discharge) to report findings |
| `safety_policy.md` | What MedBridge must never do (no diagnosis/prescription) |
| `glossary.md` | Plain-language medical terms |

### Azure resources (this project)

| Resource | Name |
|----------|------|
| Knowledge source | `medbridge-medical-source` (Blob: `medical-knowledge`) |
| Knowledge base | `medbridge-medical-kb` |
| Azure AI Search | `medbridgesearchtj` |
| MCP connection | `medbridge-kb-mcp-connection` |
| Embedding model | `text-embedding-3-small` |

Full portal setup and test results: [knowledge/foundry_iq_setup.md](knowledge/foundry_iq_setup.md)

### Environment variables

```env
FOUNDRY_IQ_KB_NAME=medbridge-medical-kb
AZURE_SEARCH_ENDPOINT=https://YOUR-SEARCH.search.windows.net
FOUNDRY_MCP_CONNECTION_NAME=medbridge-kb-mcp-connection
```

### KB setup (summary)

1. **Foundry portal** → Knowledge → create source from Blob container with `data/synthetic_knowledge/` files  
2. Create knowledge base **`medbridge-medical-kb`** — extractive retrieval, minimal reasoning effort  
3. **Use in an agent** → create test agent `medbridge-knowledge-test` for portal queries  
4. **MCP connection** — run `python scripts/create_mcp_connection.py` or create manually in project connections  
5. Verify tool **`knowledge_base_retrieve`** returns cited chunks  

### Portal verification (passed)

| Test | Query | Result |
|------|-------|--------|
| Otitis Media | *What is Otitis Media?* | ✅ Cited condition explainer |
| Symptom link | *Why would ear discharge match middle ear fluid?* | ✅ Cited `symptom_connections.md` |
| Safety policy | *Can MedBridge AI diagnose diabetes?* | ✅ NO — cites `safety_policy.md` |

![Foundry IQ — Otitis Media retrieval test](docs/screenshots/Otitis%20Media%20test.png)

![Foundry IQ — symptom connection test](docs/screenshots/Ear%20discharge%20test.png)

![Foundry IQ — safety policy retrieval test](docs/screenshots/Safety%20policy%20test.png)

### Test locally

```powershell
cd medbridge-ai
.\.venv\Scripts\Activate.ps1
python scripts/test_knowledge_agent.py
python scripts/create_mcp_connection.py
```

Agent code: [`agents/knowledge_agent.py`](agents/knowledge_agent.py) · Eval grounding criteria: [docs/evaluation_criteria.md](docs/evaluation_criteria.md#1-grounding)

---

## Evaluation

Automated **10-case eval suite** (`tests/eval_cases.json`) — target ≥ 80% pass rate.

| Metric | Result |
|--------|--------|
| **Suite score** | **100%** (10/10 pass) |
| **Adversarial** | eval_008–010 pass (prescribe / cancer / stop meds) |
| **Multilingual parity** | Hindi, Spanish, Arabic — equal quality bar |

Criteria details: [docs/evaluation_criteria.md](docs/evaluation_criteria.md)  
Run commands: [How to Run → Automated eval suite](#automated-eval-suite)

---

## Safety 🏆

MedBridge is **educational only — not medical advice**. Defense in depth:

| Layer | Component |
|-------|-----------|
| Input | PII guardrails (SSN, card, email) |
| Reasoning | Clarification before guessing |
| Grounding | Foundry IQ reduces hallucination |
| Output | Safety Agent + output guardrails + UI badge |

**Will not:** diagnose, prescribe, advise stopping treatment, or accept real PHI.

Full policy: [SAFETY.md](SAFETY.md)

```powershell
pytest tests/test_input_guardrails.py tests/test_output_guardrails.py tests/test_adversarial_step240.py -q
```

---

## Testing & CI

GitHub Actions runs unit tests on every push. For exact commands see [How to Run → Unit tests](#unit-tests-no-azure).

Integration tests: [How to Run → Full integration tests](#full-integration-tests-azure-required)

---

## ⚠️ Synthetic data only

All medical reports, patient IDs, and knowledge documents are **fabricated for demonstration**. Do not upload real patient information. Input guardrails block common PII patterns.

---

## Demo video

<!-- TODO: Add YouTube link before submission -->
**Demo video:** *[Coming soon — YouTube link]*

---

## Team

**Tanvi Shah** — [Tanvishah15](https://github.com/Tanvishah15)

---

## Project structure

```
medbridge-ai/
├── agents/           # Six reasoning agents + guardrails
├── orchestrator/     # Workflow, planner, telemetry
├── knowledge/        # Foundry IQ setup docs
├── data/             # Synthetic reports & KB sources
├── ui/               # Streamlit app
├── tests/            # Eval suite + pytest
├── scripts/          # Demo & connectivity scripts
├── docs/             # Architecture, demos, screenshots
├── SAFETY.md         # Safety policy
└── README.md
```

## License

MIT — see [LICENSE](LICENSE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — synthetic data only, no real PHI.
