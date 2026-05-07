---
title: Aarogya
emoji: 🌿
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: true
license: apache-2.0
short_description: AI Health Companion for ASHA Workers (Gemma 4)
---

# 🌿 Aarogya — AI Health Companion

**Empowering 1 million ASHA Workers with Gemma 4**

> Built for the [Gemma 4 Good Hackathon](https://kaggle.com/competitions/gemma-4-good-hackathon) — Kaggle × Google DeepMind

[![Demo](https://img.shields.io/badge/Live%20Demo-HuggingFace%20Space-orange)](https://huggingface.co/spaces/sk3306/aarogya)
[![Code](https://img.shields.io/badge/Code-GitHub-black)](https://github.com/shabdkumar3/aarogya)
[![Video](https://img.shields.io/badge/Demo%20Video-YouTube-red)](https://youtube.com/)

---

## The Problem

India has **1.07 million ASHA workers** — the primary healthcare touchpoint for 600 million rural citizens. They have no AI diagnostic support. When they encounter an unfamiliar condition, they guess. When a patient misses medications for a week, no one knows.

**Aarogya changes this.**

---

## What Aarogya Does

Aarogya is an AI health companion with two modes:

### ASHA Worker Mode (for trained health workers)
| Feature | Description |
|---|---|
| **DiagnoScan** | Upload patient photo + describe symptoms → structured triage in Hindi/English/Tamil/Telugu/Bengali |
| **MedTrack** | Log daily medication adherence → Gemma 4 detects at-risk patients via native function calling |
| **Dashboard** | All patients grouped by risk status (At Risk / Needs Attention / Stable / New) |
| **PDF Reports** | Per-patient health summary for doctor visits — AI-written clinical summary |

### Patient Lite Mode (for direct patient use)
- No registration, no IDs, no complexity
- Describe symptoms by text or voice → plain conversational Hindi/English guidance
- Audio output for low-literacy users

---

## Gemma 4 Capabilities Used

| Capability | Where Used |
|---|---|
| **Multimodal** (image + text) | DiagnoScan — rash/wound photo + Hindi description → JSON triage |
| **Native Function Calling** | MedTrack — 4 tools: `get_adherence_summary`, `flag_at_risk`, `suggest_barrier`, `generate_followup_note` |
| **Multilingual** (5 languages) | All modules — Hindi, English, Tamil, Telugu, Bengali input + output |
| **Edge Deployment** | Ollama Gemma 4 E4B — fully offline mode for rural connectivity |
| **Fine-tuned Weights** | DiagnoScan — Unsloth QLoRA on medical dataset for structured JSON triage |

---

## Architecture

```
ASHA Worker / Patient
        │
        ▼
  Gradio UI (6 tabs)
        │
   ┌────┴────┐
   │         │
ASHA Mode  Patient Lite Mode
   │         │
   └────┬────┘
        │
  LLM Client Layer (llm/client.py)
   ┌────┴─────────────────┐
   │                      │
Google AI Studio       Ollama (local)
Gemma 4 27B            Gemma 4 E4B
        │
Fine-tuned 4B (DiagnoScan)
        │
   ┌────┴────┐
   │         │
SQLite    Voice Pipeline
(local)   Whisper STT + gTTS TTS
```

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/aarogya.git
cd aarogya
pip install -r requirements.txt

# Also install ffmpeg for Whisper voice input:
# Ubuntu: sudo apt install ffmpeg
# Mac: brew install ffmpeg
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY from https://aistudio.google.com/apikey
```

### 3. Seed Demo Data & Run

```bash
python assets/demo_patients.py   # loads 4 demo patients
python app.py                     # launches on http://localhost:7860
```

### Offline Mode (Ollama)

```bash
ollama pull gemma4           # download Gemma 4 E4B
# Set MODEL_MODE=ollama in .env
python app.py
```

---

## Fine-Tuning (Optional)

Run in a Kaggle notebook with GPU T4 × 2:

```bash
pip install unsloth trl transformers datasets torch bitsandbytes
python finetuning/prepare_dataset.py   # prepares 5000 training samples
python finetuning/train.py             # ~60 min on T4
python finetuning/evaluate.py          # prints ablation table
```

**Dataset:** ChatDoctor-HealthCareMagic-100k  
**Method:** Unsloth QLoRA, r=16, 300 steps  
**Goal:** Consistent structured JSON triage output with correct urgency classification

---

## File Structure

```
aarogya/
├── app.py                    # Entry point
├── requirements.txt
├── .env.example
├── database/
│   ├── schema.py             # SQLite table definitions
│   └── queries.py            # All DB read/write functions
├── llm/
│   ├── client.py             # Gemma 4 API + Ollama routing
│   ├── prompts.py            # All prompt templates
│   └── tools.py              # Function calling definitions
├── modules/
│   ├── patient.py            # Patient CRUD
│   ├── diagnoscan.py         # Multimodal triage
│   ├── medtrack.py           # Medication tracking
│   ├── dashboard.py          # Dashboard aggregation
│   ├── patient_lite.py       # Patient Lite Mode
│   ├── voice.py              # Whisper STT + gTTS TTS
│   └── reports.py            # PDF generation
├── ui/                       # Gradio tab components
├── finetuning/               # Unsloth QLoRA pipeline
└── assets/
    └── demo_patients.py      # Demo data seed script
```

---

## Ethical Considerations

- **Not a diagnostic device.** All outputs are explicitly labelled as triage support.
- **Data privacy.** Patient data stays in a local SQLite file. Nothing is sent to cloud storage.
- **Designed to assist, not replace.** ASHA workers are trained professionals. Aarogya augments their judgment.
- **Dataset bias.** Training data is primarily English/Western context. Performance may vary for conditions more common in rural India.

---

## Medical Disclaimer

⚠️ Aarogya provides triage support only. It does not replace clinical diagnosis by a qualified doctor. All findings should be verified by a qualified healthcare professional.

---

*Built with Gemma 4 · Unsloth · Ollama · Gradio · SQLite · Whisper · gTTS · ReportLab*
