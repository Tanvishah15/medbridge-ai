# Sample Agent Outputs (Step 177)

Synthetic demo outputs for README and judge demos. Run test scripts to regenerate live output.

## Document Intelligence Agent

**Input:** `data/synthetic_reports/rpt_blood_001.txt`

**Output (structured):**
```json
{
  "diagnosis": "Type 2 Diabetes and dyslipidemia",
  "findings": ["Fasting Glucose 142 mg/dL (Elevated)", "HbA1c 7.1% (Elevated)", "LDL 168 mg/dL (Elevated)"],
  "affected_area": "Metabolic / laboratory",
  "recommendations": ["Follow up with primary care within 2 weeks", "Repeat labs in 3 months"]
}
```

## Medical Knowledge Agent

**Query:** `What is Otitis Media?`

**Output (excerpt):**
> Otitis media is an infection or inflammation of the middle ear... 【source: otitis_media.md】

## Clarification Agent

**Input:** Hindi patient, incomplete symptoms

**Output:**
1. Kya aapko bukhar hai?
2. Dard kitna hai — halka ya tez?
3. Kitne din se yeh ho raha hai?

**Input:** Complete symptoms → `[]` (skipped)

## Patient Explanation Agent

**Output (simple literacy, excerpt):**
> I understand ear discharge can feel worrying. Your report shows fluid in the middle ear, which can match what you describe. Please follow up with your doctor as recommended.

## Multilingual Agent

**Spanish (family audience, excerpt):**
> Su informe muestra líquido en el oído medio... Consulte a su médico. Esta información es educativa, no es consejo médico.

## Safety Agent

**Unsafe input:** `You definitely have diabetes. Stop your medication.`

**Output:** `safe=false`, revised response with doctor disclaimer.

**Safe input:** Passes through unchanged with `safe=true`.

---

### Regenerate Live Outputs

```powershell
python scripts/test_document_agent.py
python scripts/test_knowledge_agent.py
python scripts/test_clarification_agent.py
python scripts/test_explanation_agent.py
python scripts/test_multilingual_agent.py
python scripts/test_safety_agent.py
python scripts/profile_agents.py
```

For README screenshots, run:

```powershell
pip install playwright
python -m playwright install chromium
python scripts/capture_ui_screenshots.py --local
```

Or capture from the live cloud app (home screen only if iframe blocks automation):

```powershell
python scripts/capture_ui_screenshots.py --url https://medbridge-ai.streamlit.app
```
