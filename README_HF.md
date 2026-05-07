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

# Aarogya — AI Health Companion

Multimodal · Multilingual · Native Function Calling · Edge-ready
Built on **Gemma 4** for the Gemma 4 Good Hackathon (Health & Sciences track).

## Setup on HuggingFace
1. Add a Secret named **`GOOGLE_API_KEY`** with your Google AI Studio key (get one free at https://aistudio.google.com/apikey)
2. The Space will auto-build and launch on port 7860

## Architecture
- 6 modules: Patient Registry · DiagnoScan (vision triage) · MedTrack (function-calling) · Dashboard · Patient Self-Check (voice-first) · PDF Reports
- All AI calls route through `gemma-4-31b-it` (Gemini API) with offline Ollama fallback
- 4 demo patients seeded automatically on first launch

See full repo + writeup: https://github.com/YOUR_USERNAME/aarogya
