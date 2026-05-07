# Aarogya — Submission Deployment Guide

11 days to deadline. Follow this exact order. Each step has copy-pasteable commands.

---

## STEP 1 — Push code to GitHub (15 min)

You need this before everything else. The Kaggle writeup, the HF Space, and the finetuning notebook all link to it.

### 1a. Create the GitHub repo
1. Go to https://github.com/new
2. Name: `aarogya` · Public · **don't** add README/license (we have one)
3. Click *Create repository*

### 1b. Push from your terminal (PowerShell)
```powershell
cd "C:\Users\vishe\Pictures\New folder (2)\gemma for good\aarogya"

git init
git branch -M main
git add .
git commit -m "Initial commit — Aarogya for Gemma 4 Good Hackathon"
git remote add origin https://github.com/YOUR_USERNAME/aarogya.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub handle. Done — your repo is now public.

---

## STEP 2 — Deploy live demo on HuggingFace Space (20 min)

Free, no credit card, runs your Gradio app on a public URL.

### 2a. Create the Space
1. Go to https://huggingface.co/new-space
2. Name: `aarogya` · License: Apache 2.0 · **SDK: Docker** · Hardware: CPU basic (free)
3. Click *Create Space*

### 2b. Add your API key as a Secret
On the Space page → **Settings** tab → **Variables and secrets** → *New secret*
- Name: `GOOGLE_API_KEY`
- Value: your Gemini key

### 2c. Push your code to the Space
```powershell
cd "C:\Users\vishe\Pictures\New folder (2)\gemma for good\aarogya"

# Use the HF README (has the YAML frontmatter HF needs)
copy README_HF.md README.md /Y

git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/aarogya
git push hf main
```

The Space will auto-build (5–10 min). Your live demo URL: `https://huggingface.co/spaces/YOUR_USERNAME/aarogya`

---

## STEP 3 — Run finetuning on Kaggle GPU (90 min)

Required for the **Unsloth $10K Special Track**.

1. Go to https://www.kaggle.com/code → *New Notebook*
2. Settings (right panel): **Accelerator → GPU T4 × 2** · Internet → On
3. Click *File → Upload notebook* → upload `finetuning/AAROGYA_KAGGLE.ipynb`
4. In the second cell, replace `YOUR_USERNAME` with your GitHub handle
5. Click *Run All* — wait ~60–90 minutes
6. When done: *File → Save Version → Save & Run All* (this makes the notebook public)
7. Copy the notebook URL — you'll attach it to the writeup

The notebook produces:
- `/kaggle/working/aarogya-gemma4-lora` — LoRA adapter (50 MB)
- `/kaggle/working/aarogya-gemma4-gguf` — Quantized GGUF for Ollama
- Ablation table (base vs fine-tuned) for the writeup

---

## STEP 4 — Record the 3-min demo video (4 hours)

Follow `VIDEO_SCRIPT.md`. Quick checklist:

- **Tool:** OBS Studio (free) or Loom — record screen at 1920×1080
- **Audio:** clean voiceover, no background noise. Record voice separately, sync after
- **Open with the problem** (0:00–0:30): an ASHA worker walking between huts at sunrise
  - You can use any free B-roll from Pexels: search "rural india health"
- **Show the actual app** (0:30–2:30): walk through Patient Lite → DiagnoScan → MedTrack → Dashboard
  - Use the dark-theme app on your screen, real Gemma 4 responses
- **Close with impact + tech stack** (2:30–3:00): "Built on Gemma 4 31B, fine-tuned with Unsloth, runs offline via Ollama"

Upload to YouTube as **Unlisted** is fine (the link works for judges without login).

---

## STEP 5 — Take the cover image (5 min)

Required by Kaggle Media Gallery.

1. Open your live HF Space (or local app on http://localhost:7860)
2. Go to the **Dashboard** tab — it has the most visual content (risk badges, tables)
3. Take a clean 1920×1080 screenshot (Windows: `Win+Shift+S`)
4. Save as `aarogya_cover.png`

---

## STEP 6 — Submit on Kaggle (15 min)

1. Go to https://www.kaggle.com/competitions/gemma-4-good-hackathon
2. Click **New Writeup** (top right)
3. **Title:** `Aarogya — AI Health Companion for ASHA Workers`
4. **Subtitle:** `Multimodal Gemma 4 triage in 5 Indian languages — runs offline`
5. **Track:** select **Health & Sciences**
6. Paste the contents of `KAGGLE_WRITEUP.md` into the body
7. **Attachments → Project Links:**
   - Code: `https://github.com/YOUR_USERNAME/aarogya`
   - Live Demo: `https://huggingface.co/spaces/YOUR_USERNAME/aarogya`
   - Finetuning Notebook: your Kaggle notebook URL
8. **Media Gallery:**
   - Cover image: `aarogya_cover.png`
   - Video: paste the YouTube URL
9. Click **Save** → then **Submit**

Done. You can re-edit and re-submit any time before May 19.

---

## Quick sanity checks before submitting

- [ ] GitHub repo loads in incognito (no login needed)
- [ ] HF Space loads in incognito and the **Dashboard** tab shows demo patients
- [ ] YouTube video plays without login
- [ ] Kaggle notebook is *public* (the share link opens for someone else)
- [ ] `.env` is **NOT** in the GitHub repo (`.gitignore` covers this — verify)
- [ ] Track is selected on the writeup (`Health & Sciences`)
