# Aarogya: AI Health Companion for ASHA Workers Using Gemma 4

**Track: Health & Sciences**

---

## The Problem

India has 1.07 million ASHA (Accredited Social Health Activist) workers — the primary healthcare touchpoint for over 600 million rural citizens. They walk door to door in villages with no diagnostic tools, no connectivity, and no AI assistance. When they encounter an unfamiliar skin condition, they guess. When a patient has silently missed tuberculosis medication for two weeks, no one knows until it is too late.

This is not a technology gap. It is a gap in where technology has been deployed. Aarogya exists to close it.

---

## Solution Overview

Aarogya is an AI health companion built on Gemma 4 with two user modes:

**ASHA Worker Mode** — a full-featured clinical support tool with four modules: DiagnoScan (multimodal triage), MedTrack (medication adherence with native function calling), Dashboard (patient risk stratification), and PDF Reports (doctor-ready summaries).

**Patient Lite Mode** — a single-screen interface requiring no registration, supporting voice input and audio output, designed for patients with low literacy who need guidance in their own language.

Both modes run on the same Gemma 4 backend and support full offline operation via Ollama Gemma 4 E4B, meaning the application works in villages with no internet connectivity.

---

## Gemma 4 Capabilities

### 1. Multimodal — DiagnoScan

DiagnoScan accepts a photo of the patient's condition alongside a symptom description. Gemma 4's native multimodal understanding processes both simultaneously and returns a structured JSON triage report with urgency level (Monitor at Home / Visit PHC / Emergency Referral), possible conditions, next steps, red flags, and a specific note for the ASHA worker.

The critical design choice here was forcing JSON output rather than free text. ASHA workers need structured, scannable information — not a paragraph. The prompt enforces exact JSON schema and urgency vocabulary, and the module includes a robust parser that handles markdown-wrapped JSON gracefully.

### 2. Native Function Calling — MedTrack

MedTrack is where Gemma 4's function calling capability directly drives clinical decision-making. When an ASHA worker requests an adherence analysis, the system passes seven days of medication logs to Gemma 4 alongside four tool definitions:

- `get_adherence_summary` — computes overall compliance rate
- `flag_at_risk` — triggers when any medication has 3+ consecutive missed days
- `suggest_barrier` — reasons about the likely cause of non-adherence (forgetfulness vs. side effects vs. financial barriers)
- `generate_followup_note` — produces a specific action recommendation (home visit, phone call, counseling, referral)

Gemma 4 calls these tools in a two-turn API round-trip, then synthesizes the results into a concrete follow-up plan for the ASHA worker in the patient's preferred language. This is not a chatbot — it is an agentic workflow driving real clinical action.

### 3. Multilingual — Five Indian Languages

All modules respond in the patient's registered language preference: Hindi, English, Tamil, Telugu, or Bengali. The Patient Lite Mode prompt specifically enforces conversational vocabulary — "bukhar" not "jwara", everyday words that patients actually use — because jargon defeats the purpose.

### 4. Edge Deployment — Ollama Gemma 4 E4B

By setting `MODEL_MODE=ollama` in the configuration, Aarogya routes all LLM calls to a locally running Gemma 4 E4B instance via Ollama. This enables full offline operation: no API key, no internet, no patient data leaving the device. For a rural ASHA worker with intermittent connectivity, this is the difference between a usable tool and an unusable one.

---

## Fine-Tuning with Unsloth

The base Gemma 4 4B model occasionally wraps JSON in markdown fences or outputs explanatory prose before the JSON object, which breaks the DiagnoScan parser. To fix this, we fine-tuned Gemma 4 4B using Unsloth QLoRA on a medical Q&A dataset.

**Dataset:** ChatDoctor-HealthCareMagic-100k (5,000 training samples, 800 validation)  
**Method:** Unsloth QLoRA, r=16, lora_alpha=16, 300 training steps on Kaggle T4 GPU  
**Goal:** Teach the model to produce clean, structured JSON triage from symptom descriptions with correct urgency classification

Training time was approximately 60 minutes on a T4. Unsloth's memory optimization allowed 2× larger effective batch size versus standard PEFT on the same hardware.

**Ablation Results (evaluate.py):**

| Metric | Base Gemma 4 4B | Aarogya Fine-tuned 4B |
|---|---|---|
| Correct urgency classification | [Run evaluate.py] | [Run evaluate.py] |
| Valid JSON output | [Run evaluate.py] | [Run evaluate.py] |

*(Run `python finetuning/evaluate.py` after training to populate this table with real numbers.)*

---

## Architecture Decisions

**SQLite over a cloud database.** Patient health data is sensitive. Keeping it in a local file means zero cloud exposure and zero ongoing cost. For an ASHA worker's device, this is also faster.

**Gradio over a custom frontend.** Gradio's tab layout maps directly to ASHA worker workflows and can be shared via a public URL in one line of code. Iteration speed was critical for a hackathon.

**ReportLab for PDFs.** ASHA workers need a physical artefact to hand to PHC doctors who may not have internet access. A structured, printed PDF is more practical than a shared link in rural India.

**Whisper for STT.** OpenAI Whisper runs fully offline and supports Hindi, Tamil, Telugu, and Bengali. It is the only viable STT option for this use case.

---

## Challenges Overcome

The hardest challenge was prompt engineering for multilingual JSON. Getting Gemma 4 to produce valid JSON with urgency values in exactly the expected vocabulary ("Visit PHC" not "visit the PHC" not "go to PHC") while also translating all values into Hindi required iterative prompt testing. The solution was enforcing exact vocabulary in the system prompt and adding a fallback JSON parser for edge cases.

The second challenge was the Ollama function calling gap. Ollama's Gemma 4 E4B does not currently support native function calling. Rather than disabling MedTrack in offline mode, we implemented a structured text fallback that produces a similar clinical output using a detailed prompt. Offline users get slightly less structured output but full functionality.

---

## Real-World Impact Potential

Aarogya targets a specific, measurable gap: the 1.07 million ASHA workers who currently have no AI support. A tool that helps one ASHA worker correctly identify one emergency referral that would have been sent home has immediate life impact. A tool that tracks medication adherence across a village of 200 people and flags the three patients most at risk of treatment failure has systemic health impact.

The application is designed for immediate deployment: it runs on any Android tablet with Python, requires no server infrastructure, and costs nothing per inference in offline mode.

---

## Limitations

1. Image quality dependency: DiagnoScan accuracy depends on photo quality from low-end phones
2. Training data bias: Base dataset is English/Western medical context; performance on India-specific conditions (dengue, typhoid, malnutrition) should be validated
3. gTTS requires internet: Audio output falls back to text in offline mode
4. Not validated clinically: Aarogya is a proof-of-concept, not a regulated medical device

---

## Future Work

1. Fine-tune on Hindi medical datasets (MedMCQA, Ayurvedic knowledge bases)
2. Integration with NHM ASHA portal for national scale
3. SMS-based adherence logging for patients without smartphones
4. Expand to 22 scheduled Indian languages via IndicTrans2
5. Pilot deployment with state health departments

---

*Code: github.com/YOUR_USERNAME/aarogya | Demo: huggingface.co/spaces/YOUR_USERNAME/aarogya*
