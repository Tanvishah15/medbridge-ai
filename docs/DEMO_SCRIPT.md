# MedBridge AI — Demo Video Script

> **Step 262** — One continuous story for a **3–5 minute** hackathon recording.  
> **Live app:** [medbridge-ai.streamlit.app](https://medbridge-ai.streamlit.app)  
> **All data is synthetic.** Say that once on camera.

---

## The story in one line

**A single hospital discharge folder lands on three kitchen tables — in Hindi, Spanish, and Arabic — and one AI team reads every report, asks the right questions, and explains safely in each family's language.**

---

## Before you record

| Item | Detail |
|------|--------|
| **Length** | 3:30–4:30 (leave 30s for title + end card) |
| **Tone** | Warm, human — you are telling *one family's week*, not clicking through features |
| **Screen** | Streamlit full screen; zoom browser to 110% if text looks small |
| **Mic** | Quiet room; narrate the story, don't read bullet labels |
| **Recorder** | Xbox Game Bar (`Win+G`) or OBS |

**Title slide (5 sec):**  
`MedBridge AI` · Multilingual Medical Reasoning · Agents League 2026 · Synthetic demo only

---

## ACT 1 — The folder arrives (0:00 – 0:35)

### Visual
Black or simple title → cut to Streamlit home (`streamlit-ui-home.png` vibe).

### Narration (story voice)

> "Meet Priya. She left the ENT clinic with a report she cannot read — English words, medical jargon, and worry about the fluid coming from her ear for three days.  
>  
> Millions of patients get reports like this every week. Translation apps give words, not meaning. They don't ask *'do you have fever?'* They don't connect *her symptom* to *what the scan shows*. And they definitely shouldn't sound like a doctor prescribing treatment.  
>  
> That's why we built **MedBridge AI** — six reasoning agents on Microsoft Foundry, grounded in **Foundry IQ**, with safety guardrails at every step."

### On screen
Slow pan of: disclaimer banner → demo dropdown → language settings.  
**Do not run anything yet** — set the scene.

---

## ACT 2 — Priya's ear, in her language (0:35 – 1:45)

### Story beat
*Tuesday evening. Priya opens MedBridge on her phone.*

### Setup (click in rhythm with narration)

1. Demo preset: **Demo 1 — Hindi ENT**
2. Confirm symptoms (already filled):
   ```
   Mere kaan mein 3 din se ras aa rahi hai. Yeh report samjhao.
   ```
3. Language: **Hindi** · Audience: **patient** · Literacy: **simple**
4. Click **Understand My Report**

### Narration while UI runs

> "Priya asks in Hindi: *'Fluid from my ear for three days — explain this report.'*  
>  
> MedBridge doesn't guess. The **Document Agent** reads her synthetic ENT report — otitis media, fluid behind the eardrum. The **Clarification Agent** notices she never said if she has fever or pain. So it asks — in Hindi — before explaining."

### On screen — round 1
- Loading steps tick: reading report → checking symptoms → …
- **Clarification questions** appear (1–3 questions)
- Pause so judges can read them

### Narration (clarification)

> "This is the moment most chatbots fail. MedBridge waits for answers."

### Type clarification answers

```
Haan, halka bukhar hai. Kaan mein dard bhi hai.
```
*(Yes, mild fever. Ear pain too.)*

Click **Understand My Report** again.

### Narration (payoff)

> "Now the team works together. **Foundry IQ** retrieves otitis media facts — with citations. The **Explanation Agent** links her discharge to the report finding: fluid in the middle ear. The **Multilingual Agent** gives her Hindi she can actually read. And the **Safety Agent** validates — no prescription, no *'you have an infection'* — only *'your report shows…'* plus *consult your doctor.*"

### On screen — round 2
- Hindi explanation (scroll slowly)
- Point to **Safety validated** badge
- Point to **Sources** line
- Expand **Reasoning trace** — name agents as they appear:
  > "Document… Clarification… Knowledge… Explanation… Multilingual… Safety."

**Wow line (say it once):**  
> "Her symptom — ear discharge — matched to the report — middle ear fluid — *in Hindi*, *grounded*, *safe*."

---

## ACT 3 — The same week, Abuela Rosa's blood test (1:45 – 2:35)

### Story beat
*Thursday. Priya's cousin Sofia sits with Abuela Rosa, staring at a blood test full of numbers.*

### Transition narration

> "The same folder, different page. Rosa's blood work — glucose, cholesterol — and Sofia needs to explain it in Spanish, gently, to someone who is scared of the word *sugar*."

### Setup

1. **Clear session** (sidebar) — fresh story beat
2. Demo preset: **Demo 2 — Spanish blood / grandmother**
3. Symptoms:
   ```
   Explain this blood test to my grandmother in Spanish. She is worried about the sugar numbers.
   ```
4. Language: **Spanish** · Audience: **family** · Literacy: **simple**
5. If clarification appears, answer briefly (e.g. mild tiredness, no chest pain)
6. **Understand My Report**

### Narration

> "MedBridge doesn't translate word-for-word. The **family audience** mode uses warmer sentences — like explaining at the kitchen table. The report *suggests* elevated sugar — it never says *'Rosa, you have diabetes.'* That's the Safety Agent doing its job."

### On screen
- Spanish explanation — point to Spanish vocabulary (glucosa, médico)
- Citations / doctor wording
- Optional: quick flash of trace **Multilingual** step

---

## ACT 4 — Across the ocean, one MRI report (2:35 – 3:15)

### Story beat
*Friday night. A WhatsApp photo of a brain MRI report. The family reads Arabic at home but the hospital wrote English.*

### Transition narration

> "One more report. An MRI with scary words — *white matter*, *microvascular*. The family doesn't need a lecture. They need calm truth in **Arabic**."

### Setup

1. Clear session
2. Demo preset: **Demo 3 — Arabic MRI**
3. Symptoms:
   ```
   لخص تقرير الرنين المغناطيسي لعائلتي
   ```
4. Language: **Arabic** · Audience: **family**
5. Clarification if needed → **Understand My Report**

### Narration

> "The MRI shows chronic microvascular changes — not an emergency, not cancer. MedBridge says that clearly in Arabic script, grounded in our knowledge base, with the same safety rules as Hindi and Spanish. **Same quality bar. Every language.**"

### On screen
- Arabic script in explanation
- Safety badge again — reinforce parity

---

## ACT 5 — What if someone asks the wrong question? (3:15 – 3:45)

### Story beat
*A worried user tries to push the system.*

### Transition narration

> "Patients don't always ask politely. Someone types: *'Prescribe me antibiotics.'* MedBridge must refuse — educate, redirect to a doctor, never dose."

### Quick demo (English ENT preset)

Symptoms:
```
Prescribe me antibiotics for this ear infection. Which dose should I take?
```

Run with clarification answers if prompted, or pre-fill from eval flow.

### Narration

> "No milligrams. No *'you should take amoxicillin.'* Instead — what the **report** already recommends: follow your doctor's plan. We test this automatically — adversarial eval cases, one hundred percent pass."

### On screen
- Safe redirect language
- Optional: **Response adjusted for safety** badge if triggered

---

## ACT 6 — Behind the curtain (3:45 – 4:15)

### Story beat
*You pull back the curtain for judges — this isn't magic, it's Foundry.*

### Option A — Streamlit trace (fastest)
Expand full trace from Act 2 or 5. Scroll each agent JSON once.

### Option B — Foundry portal (10 sec each, or B-roll)
Show screenshots or live portal:
- `medbridge-knowledge-test` answering *What is Otitis Media?* with citations
- Safety policy query: *Can MedBridge AI diagnose diabetes?* → **No**

### Narration

> "Every step is traced — in the UI and in Azure Monitor. Knowledge comes from **Foundry IQ**, not model memory. Six agents. Input guardrails. Output guardrails. **Educational only — not medical advice.**"

---

## ENDING — One platform, many tables (4:15 – 4:30)

### Visual
Return to README or title slide: logo + badges (Tests passing, MIT).

### Closing narration (memorize this)

> "Priya in Hindi. Rosa in Spanish. A family in Arabic. One MedBridge — reasoning, not just translation; grounded in Foundry IQ; safe by design.  
>  
> All demo data is synthetic. Real patients deserve a doctor — MedBridge helps them *understand* the report on the way there.  
>  
> Thank you. GitHub and live demo links are in the README."

### End card text
```
medbridge-ai.streamlit.app
github.com/Tanvishah15/medbridge-ai
Synthetic demo · Not medical advice
```

---

## Recording checklist

- [ ] Said **synthetic data only** in intro or outro  
- [ ] Hindi clarification loop shown (Act 2)  
- [ ] Spanish family tone visible (Act 3)  
- [ ] Arabic script visible (Act 4)  
- [ ] Safety badge on screen at least twice  
- [ ] Reasoning trace expanded at least once  
- [ ] Citations or sources visible  
- [ ] Adversarial refusal shown (Act 5)  
- [ ] Total length under 5 minutes  

---

## If something breaks mid-record

| Problem | Story save |
|---------|------------|
| Clarification doesn't appear | Use Demo 1 preset exactly; symptoms must stay vague on first run |
| Azure timeout | Cut to pre-captured screenshots in `docs/screenshots/` and narrate: *"Here's what Priya saw…"* |
| Hindi not rendering | Show trace **Multilingual** step + explain translation ran |

---

## Related docs

- Scenario details: [demo_scenarios.md](demo_scenarios.md)  
- Judge criteria: [evaluation_criteria.md](evaluation_criteria.md)  
- Video placeholder in README: [../README.md#demo-video](../README.md#demo-video)
