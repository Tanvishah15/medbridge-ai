# Foundry IQ Setup — MedBridge AI

> Document your knowledge base configuration here (Step 111).

## Knowledge Source
- **Name:** `medbridge-medical-source`
- **Type:** Azure Blob Storage
- **Storage account:** `medbridgestoragetj`
- **Container:** `medical-knowledge`

## Knowledge Base
- **Name:** `medbridge-medical-kb`
- **Retrieval:** Minimal
- **Data type:** Extractive
- **Model:** gpt-4.1-mini

## Azure AI Search
- **Service:** `medbridgesearchtj`
- **Region:** East US
- **Tier:** Free

## Test Agent
- **Name:** `medbridge-knowledge-test`
- **Sample query:** "What is Otitis Media?" — verified working

## MCP Connection
- RemoteTool connection for `knowledge_base_retrieve` — to be configured in Phase 5 (Step 112)

## Screenshots
_Add portal screenshots here during Step 111._
