# Aarogya — Demo Video Script
## 3 Minutes | Optimized for Impact & Vision (40pts) + Storytelling (30pts)

---

### BEFORE YOU RECORD

- Seed the database first: `python assets/demo_patients.py`
- Have a real photo of a skin condition ready (rash, wound, etc.)
- Set response language to Hindi for DiagnoScan
- Keep the terminal hidden; show only the Gradio UI
- Record at 1080p, use OBS or Loom

---

## SCENE 1 — THE HOOK (0:00–0:25)

**[Show: Black screen with text, then cut to a map of rural India]**

**Say (voice over):**
> "There are one million women in India who are the only healthcare worker their village will ever see. They walk door to door with no tools, no support, no AI. When they see a rash they don't recognize — they guess. When a patient stops taking their tuberculosis medication — no one knows. My name is [YOUR NAME], and this is Aarogya."

**[Cut to: Aarogya app loading on screen]**

> "An AI health companion for ASHA workers — powered by Gemma 4."

---

## SCENE 2 — DIAGNOSCAN: MULTIMODAL TRIAGE (0:25–1:10)

**[Show: Patient Registry tab — Ramesh Kumar already registered]**

**Say:**
> "Meet Ramesh Kumar. 52 years old, diabetic, from a village in Rajasthan. His ASHA worker has noticed a rash on his leg."

**[Click DiagnoScan tab. Select Ramesh from dropdown.]**

> "She uploads a photo and describes the symptoms in Hindi."

**[Type in Hindi: "Pair mein laal daane hain, khaaj ho rahi hai, 3 din se hai"]**
**[Upload the rash photo. Click Run DiagnoScan.]**

> "Gemma 4 processes the image AND the Hindi text together — natively multimodal."

**[Show: Result appears — urgency, conditions, next steps, red flags in Hindi]**

> "In seconds — urgency level, possible conditions, exact next steps, red flags to watch for — all in Hindi. Structured. Actionable. Saved to the patient record."

---

## SCENE 3 — MEDTRACK: FUNCTION CALLING (1:10–1:55)

**[Click MedTrack tab. Select Ramesh.]**

**Say:**
> "Ramesh is also on Metformin for his diabetes. He's missed 4 consecutive days."

**[Click 'Load Active Medications' — show the table]**

> "Watch what happens when we run Gemma 4's adherence analysis."

**[Click 'Run Gemma 4 Analysis'. While it loads:]**

> "This is native function calling. Gemma 4 is calling four tools simultaneously — get_adherence_summary, flag_at_risk, suggest_barrier, generate_followup_note — reasoning across the data."

**[Show: The analysis result appears — patient flagged HIGH risk, specific barrier identified, follow-up note generated]**

> "High risk. Likely barrier: cost or side effects. Recommended action: home visit this week. One click gave the ASHA worker a complete clinical action plan."

---

## SCENE 4 — DASHBOARD (1:55–2:15)

**[Click Dashboard tab. Click Refresh Dashboard.]**

**Say:**
> "The dashboard shows all patients at once — color-coded by risk."

**[Show: Red = Ramesh at risk, Yellow = Lakshmi needs attention, Green = Sunita stable]**

> "Ramesh is flagged red. Sunita Devi, on tuberculosis DOTS therapy, is green — perfect adherence. Lakshmi Bai at 57% — needs a follow-up call."

> "One ASHA worker. Twenty villages. Now she knows exactly who to visit first."

---

## SCENE 5 — PATIENT LITE MODE (2:15–2:42)

**[Click Patient Self-Check tab]**

**Say:**
> "But what about patients with no ASHA worker nearby? Patient Lite Mode."

**[Type in Hindi symptoms: "3 din se bukhar hai, sar mein dard hai, khana nahi kha raha"]**
**[Select Hindi. Click Get Guidance.]**

**[Show: Plain conversational Hindi response appears]**

> "No JSON. No medical jargon. Plain Hindi — the way a trusted neighbour would explain it."

**[Click Read Response Aloud — audio plays]**

> "And for patients who can't read — Gemma 4's response is read aloud. This is how you reach the last mile."

---

## SCENE 6 — CLOSE (2:42–3:00)

**[Show: Split screen — fine-tuning ablation table + app running side by side]**

**Say:**
> "Aarogya uses every Gemma 4 capability. Multimodal triage. Native function calling. Five Indian languages. Edge deployment via Ollama for offline villages. And a fine-tuned 4B model using Unsloth QLoRA that improves structured output accuracy."

**[Cut to: Single line on black screen]**

> "One million ASHA workers. Six hundred million patients. The technology exists. It just needed to go to the right place."

**[Show: GitHub link + HuggingFace Space link]**

---

## RECORDING TIPS

- Keep energy high in Scenes 1 and 6 — those score on Vision and Storytelling
- In Scene 3, pause 2 seconds before the result appears to build tension
- Show the actual JSON tool calls in the accordion (Raw JSON Output) briefly during Scene 2 — proves technical depth
- Total runtime target: 2:50–3:00 exactly
- Add subtitles for the Hindi portions

---

## WHAT TO SHOW ON SCREEN vs. WHAT TO SAY

| Time | Screen | Voice |
|---|---|---|
| 0:00–0:25 | Map / title card | Hook narrative |
| 0:25–1:10 | DiagnoScan live | Explain multimodal |
| 1:10–1:55 | MedTrack + analysis | Explain function calling |
| 1:55–2:15 | Dashboard | Show risk stratification |
| 2:15–2:42 | Patient Lite + audio | Show accessibility |
| 2:42–3:00 | Ablation table + links | Close with impact |
