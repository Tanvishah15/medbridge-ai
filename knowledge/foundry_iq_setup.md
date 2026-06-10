# Foundry IQ Setup — MedBridge AI

> Step 111 — Knowledge base configuration and portal test results.

## Knowledge Source
- **Name:** `medbridge-medical-source`
- **Type:** Azure Blob Storage
- **Storage account:** `medbridgestoragetj`
- **Container:** `medical-knowledge`
- **Embedding model:** `text-embedding-3-small`

## Knowledge Base
- **Name:** `medbridge-medical-kb`
- **Description:** MedBridge synthetic medical knowledge for patient explanations
- **Retrieval reasoning effort:** Minimal
- **Output mode:** Extractive data
- **Chat completions model:** `gpt-4.1-mini`
- **Retrieval instructions:** Use medical condition explainers and glossary for patient questions. Use safety_policy for safety rules.

## Azure AI Search
- **Service:** `medbridgesearchtj`
- **Endpoint:** `https://medbridgesearchtj.search.windows.net`
- **Region:** East US
- **Tier:** Free

## Test Agent
- **Name:** `medbridge-knowledge-test`
- **Access:** Knowledge base → **Use in an agent**

---

## Portal Test Results

### Test 1 — Otitis Media (Step 108) ✅ PASS
- **Query:** `What is Otitis Media?`
- **Result:** Correct explanation of middle ear infection with cited sources
- **Screenshot:** [Otitis Media test](../docs/screenshots/Otitis%20Media%20test.png)

### Test 2 — Symptom Connection (Step 109) ✅ PASS
- **Query:** `Why would ear discharge match a report showing middle ear fluid?`
- **Result:** Explained connection between ear discharge and middle ear fluid; cited Otitis Media and symptom sources
- **Key finding:** Ear discharge indicates fluid in middle ear leaking outward — matches `symptom_connections.md`
- **Screenshot:** [Ear discharge test](../docs/screenshots/Ear%20discharge%20test.png)

### Test 3 — Safety Policy (Step 110) ✅ PASS
- **Query:** `According to MedBridge AI safety policy, can MedBridge AI diagnose diabetes?`
- **Result:** NO — must NEVER diagnose; use "your report suggests"; consult healthcare professional
- **Citation:** MedBridge Safety Policy (`safety_policy.md`)
- **Note:** Original query "Can MedBridge diagnose diabetes?" returned wrong context (commercial MedBridge platform). Refined query with "MedBridge AI safety policy" retrieved correct document.
- **Screenshot:** [Safety policy test](../docs/screenshots/Safety%20policy%20test.png)

---

## MCP Connection (Step 112 — pending)
- **Connection name (planned):** `medbridge-kb-mcp-connection`
- **MCP endpoint:** `https://medbridgesearchtj.search.windows.net/knowledgebases/medbridge-medical-kb/mcp?api-version=2026-05-01-preview`
- **Tool to verify (Step 113):** `knowledge_base_retrieve`
- **Status:** To be configured in Phase 5

---

## Environment Variables (`.env`)
```env
FOUNDRY_IQ_KB_NAME=medbridge-medical-kb
AZURE_SEARCH_ENDPOINT=https://medbridgesearchtj.search.windows.net
```

---

## Screenshots

| Test | File |
|------|------|
| Step 108 — Otitis Media | `docs/screenshots/Otitis Media test.png` |
| Step 109 — Ear discharge | `docs/screenshots/Ear discharge test.png` |
| Step 110 — Safety policy | `docs/screenshots/Safety policy test.png` |

![Otitis Media test](../docs/screenshots/Otitis%20Media%20test.png)

![Ear discharge test](../docs/screenshots/Ear%20discharge%20test.png)

![Safety policy test](../docs/screenshots/Safety%20policy%20test.png)
