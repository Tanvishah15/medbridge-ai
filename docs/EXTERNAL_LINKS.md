# External Links — MedBridge AI

> **Step 263** — All external URLs referenced in this project (docs, code, README).  
> Last reviewed for hackathon submission.

---

## MedBridge project

| Link | Used in |
|------|---------|
| [Live demo — medbridge-ai.streamlit.app](https://medbridge-ai.streamlit.app) | README, DEMO_SCRIPT, Streamlit Cloud |
| [GitHub repo — Tanvishah15/medbridge-ai](https://github.com/Tanvishah15/medbridge-ai) | README, clone instructions |
| [GitHub Actions — Tests badge](https://github.com/Tanvishah15/medbridge-ai/actions/workflows/test.yml) | README CI badge |
| [shields.io — License badge](https://img.shields.io/github/license/Tanvishah15/medbridge-ai) | README MIT badge |
| [YouTube demo placeholder](https://youtu.be/REPLACE_WITH_VIDEO_ID) | README (replace after upload) |

---

## Hackathon & community

| Link | Purpose |
|------|---------|
| [Agents League Hackathon](https://github.com/microsoft/agentsleague) | Event home, rules, submission |
| [Reasoning Agents Starter Kit](https://github.com/microsoft/agentsleague/blob/main/starter-kits/2-reasoning-agents/README.md) | Track reference |
| [Agents League DISCLAIMER](https://github.com/microsoft/agentsleague/blob/main/DISCLAIMER.md) | Official disclaimer |
| [Agents League CODE_OF_CONDUCT](https://github.com/microsoft/agentsleague/blob/main/CODE_OF_CONDUCT.md) | Community standards |
| [Hackathon registration](https://info.microsoft.com/Agents-League-Hackathon-Registration.html) | Sign-up |
| [Agents League Discord](https://aka.ms/agentsleague/discord) | Community support |
| [Microsoft Reactor YouTube](https://www.youtube.com/@MicrosoftReactor) | Office hours / workshops |

---

## Microsoft Foundry & Azure (documentation)

| Link | Referenced in |
|------|----------------|
| [Microsoft Foundry portal](https://ai.azure.com) | Setup, tracing docs |
| [Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/) | Architecture |
| [Agent Framework quick start](https://learn.microsoft.com/en-us/agent-framework/tutorials/quick-start) | Development |
| [Agent Framework observability](https://learn.microsoft.com/en-us/agent-framework/agents/observability) | `docs/observability.md` |
| [What is Foundry IQ?](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-foundry-iq) | KB integration |
| [Connect Foundry IQ to Agent Service](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/foundry-iq-connect) | KB setup |
| [Multi-agent workflow concepts](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/workflow) | Orchestration |
| [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview) | Agents |
| [Evaluate AI agents (Foundry SDK)](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/evaluate-sdk) | `docs/evaluation_criteria.md` |
| [Responsible AI in Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/overview) | Safety approach |
| [Set up tracing in Foundry](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-setup) | `docs/foundry_tracing_setup.md` |
| [Trace agent frameworks](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-framework) | OTel setup |
| [Client-side tracing](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-client-side) | App Insights |
| [Azure AI Search — create service](https://learn.microsoft.com/en-us/azure/search/search-create-service-portal) | Foundry IQ backend |
| [Agentic retrieval overview](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-overview) | Retrieval |
| [Azure free account](https://aka.ms/azure-free-account) | Credits |
| [Azure for Students](https://azure.microsoft.com/free/students/) | Student credits |

---

## Tools & runtime (open source / services)

| Link | Purpose |
|------|---------|
| [Python downloads](https://www.python.org/downloads/) | Local dev (3.12+) |
| [Git for Windows](https://git-scm.com/download/win) | Version control |
| [GitHub CLI](https://cli.github.com/) | Optional PR/issues |
| [Streamlit](https://streamlit.io/) | Demo UI framework |
| [OBS Studio](https://obsproject.com/) | Demo video recording (playbook) |

---

## Azure API scopes (authentication in code)

Used by `azure-identity` in scripts — not browsable pages:

| Scope | File |
|-------|------|
| `https://cognitiveservices.azure.com/.default` | `scripts/test_auth.py`, `test_service_principal.py` |
| `https://ai.azure.com/.default` | `scripts/test_model_openai.py` |
| `https://management.azure.com/.default` | `scripts/create_mcp_connection.py` |
| `https://search.azure.com/` (MCP audience) | MCP connection setup |

---

## This project's Azure endpoints (demo deployment)

Documented in `knowledge/foundry_iq_setup.md` — **synthetic demo resources only**:

| Resource | URL |
|----------|-----|
| Azure AI Search | `https://medbridgesearchtj.search.windows.net` |
| Foundry IQ MCP | `https://medbridgesearchtj.search.windows.net/knowledgebases/medbridge-medical-kb/mcp?api-version=2026-05-01-preview` |

Replace with your own endpoints in `.env` / Streamlit Secrets for a fresh deployment.

---

## Internal doc cross-links

Not external — listed for judges navigating the repo:

- [README.md](../README.md)
- [SAFETY.md](../SAFETY.md)
- [architecture.md](architecture.md)
- [evaluation_criteria.md](evaluation_criteria.md)
- [DEMO_SCRIPT.md](DEMO_SCRIPT.md)
- [foundry_iq_setup.md](../knowledge/foundry_iq_setup.md)
