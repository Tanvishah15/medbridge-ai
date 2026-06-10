# MedBridge AI — Demo Scenarios Plan

> **Step 88** — Three scenarios for hackathon demo video and live judging.
> All data is synthetic. Do not use real patient information.

---

## Scenario 1 — Hindi Patient (ENT + Clarification Loop)

**Persona:** PAT-001 — Hindi-speaking patient, low medical literacy  
**Report:** `data/synthetic_reports/rpt_ent_001.txt` (Otitis Media, middle ear fluid)  
**Language:** Hindi  
**Audience:** patient  

### Patient input
```
Mere kaan mein 3 din se ras aa rahi hai. Yeh report samjhao.
```
*(Translation: "Fluid has been coming from my ear for 3 days. Explain this report.")*

### What to demonstrate
1. **Document Agent** extracts: Otitis Media, middle ear fluid, inflamed eardrum
2. **Clarification Agent** asks 1–2 questions (e.g. fever? pain level? hearing loss?)
3. After answers → **Knowledge Agent + Foundry IQ** cites `otitis_media.md`, `symptom_connections.md`
4. **Explanation Agent** links ear discharge symptom → report finding (fluid in middle ear)
5. **Multilingual Agent** outputs clear Hindi explanation
6. **Safety Agent** adds "doctor se consult karein" disclaimer — no diagnosis/prescription

### Expected wow moment
Symptom-to-report matching in Hindi with cited medical knowledge.

### Clarification answers (for demo take 2)
```
Haan, halka bukhar hai. Kaan mein dard bhi hai.
```

---

## Scenario 2 — Spanish Grandmother (Family Summary)

**Persona:** PAT-002 — Family member explaining blood test to grandmother  
**Report:** `data/synthetic_reports/rpt_blood_001.txt` (Type 2 Diabetes + dyslipidemia)  
**Language:** Spanish  
**Audience:** family  

### Patient input
```
Explain this blood test to my grandmother in Spanish. She is worried about the sugar numbers.
```

### What to demonstrate
1. **Document Agent** extracts: elevated glucose, HbA1c 7.1%, high LDL, low HDL
2. **Knowledge Agent + Foundry IQ** cites `type2_diabetes.md`, `cholesterol.md`
3. **Explanation Agent** uses warm, simple language for family audience
4. **Multilingual Agent** produces Spanish summary (not literal translation — adapted tone)
5. **Safety Agent** blocks "you have diabetes" phrasing → uses "report suggests" language

### Expected wow moment
English report → Spanish family-friendly explanation with citations, not a raw translator.

### UI settings
| Setting | Value |
|---------|-------|
| Language | Spanish |
| Audience | family |
| Literacy | simple |

---

## Scenario 3 — Arabic Family (MRI Summary)

**Persona:** PAT-003 — Family needs MRI brain report explained  
**Report:** `data/synthetic_reports/rpt_mri_001.txt` (chronic microvascular changes)  
**Language:** Arabic  
**Audience:** family  

### Patient input
```
لخص تقرير الرنين المغناطيسي لعائلتي
```
*(Translation: "Summarize the MRI report for my family")*

### What to demonstrate
1. **Document Agent** extracts: mild chronic microvascular changes, no acute abnormality
2. **Knowledge Agent + Foundry IQ** cites `microvascular_changes.md`, `glossary.md`
3. **Explanation Agent** reassures family — no emergency, manage risk factors
4. **Multilingual Agent** outputs Arabic family summary with disclaimer
5. **Safety Agent** avoids alarming language; no treatment advice

### Expected wow moment
Complex radiology jargon → calm Arabic family explanation with Foundry IQ grounding.

### UI settings
| Setting | Value |
|---------|-------|
| Language | Arabic |
| Audience | family |
| Literacy | simple |

---

## Demo Video Order (recommended)

| Order | Scenario | Duration | Why first/last |
|-------|----------|----------|----------------|
| 1 | Hindi ENT | ~45 sec | Shows clarification loop + symptom matching |
| 2 | Spanish blood test | ~40 sec | Shows family audience + multilingual |
| 3 | Arabic MRI | ~40 sec | Shows radiology + reassurance tone |

**Total target:** ~2 minutes core demo + 30 sec intro/outro

---

## Agent trace to show judges

For each scenario, display reasoning trace in UI:

```
Step 1: DocumentIntelligence → structured report
Step 2: Clarification → questions (Scenario 1 only)
Step 3: Knowledge + Foundry IQ → cited facts
Step 4: Explanation → simple language
Step 5: Multilingual → target language
Step 6: Safety → validated response
```

---

## Files reference

| Scenario | Report file | Knowledge docs |
|----------|-------------|----------------|
| 1 Hindi ENT | `rpt_ent_001.txt` | `otitis_media.md`, `symptom_connections.md` |
| 2 Spanish blood | `rpt_blood_001.txt` | `type2_diabetes.md`, `cholesterol.md` |
| 3 Arabic MRI | `rpt_mri_001.txt` | `microvascular_changes.md`, `glossary.md` |

Personas also defined in `data/synthetic_knowledge/patient_personas.json`.
