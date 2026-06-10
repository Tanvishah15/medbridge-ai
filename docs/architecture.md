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

## Components

| Folder | Purpose |
|--------|---------|
| `agents/` | Six specialized reasoning agents |
| `orchestrator/` | Sequential + handoff workflow |
| `knowledge/` | Foundry IQ setup documentation |
| `data/` | Synthetic reports and knowledge docs |
| `ui/` | Streamlit patient-facing app |
| `tests/` | Workflow and evaluation tests |
| `scripts/` | Auth and connectivity test scripts |

## Tech Stack
- Python 3.12
- Microsoft Agent Framework + Foundry
- Foundry IQ (Azure AI Search + Blob Storage)
- Streamlit
