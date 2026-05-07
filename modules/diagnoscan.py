import base64
import json
import os
import io
from datetime import datetime
from PIL import Image
from database.queries import (
    save_diagnosis, get_diagnoses_for_patient,
    parse_dropdown, get_patient_by_id
)
from llm.client import call_gemma_multimodal
from llm.prompts import DIAGNOSCAN_PROMPT

IMAGE_SAVE_DIR = "saved_images"
os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)

URGENCY_EMOJI = {
    "Monitor at Home": "🟢",
    "Visit PHC": "🟡",
    "Emergency Referral": "🔴"
}


def pil_to_base64(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def save_image_to_disk(image: Image.Image) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(IMAGE_SAVE_DIR, f"img_{ts}.jpg")
    image.convert("RGB").save(path, "JPEG")
    return path


def parse_json_response(raw: str):
    clean = raw.strip()
    if "```" in clean:
        parts = clean.split("```")
        for part in parts:
            stripped = part.strip()
            if stripped.startswith("json"):
                stripped = stripped[4:].strip()
            try:
                return json.loads(stripped)
            except:
                continue
    try:
        return json.loads(clean)
    except:
        return None


def run_diagnoscan(patient_dropdown, image, symptom_text, language):
    pid = parse_dropdown(patient_dropdown)
    if not pid:
        return "", "", "Please select a patient."
    if image is None:
        return "", "", "Please upload an image of the condition."
    if not symptom_text or not symptom_text.strip():
        return "", "", "Please describe the symptoms."

    patient = get_patient_by_id(pid)
    image_path = save_image_to_disk(image)
    image_b64 = pil_to_base64(image)

    prompt = DIAGNOSCAN_PROMPT.format(
        symptoms=symptom_text.strip(),
        existing_conditions=patient.get("conditions", "None"),
        allergies=patient.get("allergies", "None"),
        language=language
    )

    raw_response, model_used = call_gemma_multimodal(prompt, image_b64)

    if raw_response is None:
        return "", "", "LLM call failed. Check API key or Ollama connection."

    parsed = parse_json_response(raw_response)
    if parsed is None:
        return "", raw_response, "Could not parse model response. Raw output shown."

    save_diagnosis(
        patient_id=pid,
        image_path=image_path,
        symptom_description=symptom_text.strip(),
        raw_response=raw_response,
        conditions=", ".join(parsed.get("conditions", [])),
        urgency=parsed.get("urgency", "Unknown"),
        next_steps="; ".join(parsed.get("next_steps", [])),
        red_flags="; ".join(parsed.get("red_flags", [])),
        model_used=model_used
    )

    urgency = parsed.get("urgency", "Unknown")
    emoji = URGENCY_EMOJI.get(urgency, "⚪")
    conditions = "\n".join(f"- {c}" for c in parsed.get("conditions", []))
    next_steps = "\n".join(f"- {s}" for s in parsed.get("next_steps", []))
    red_flags = "\n".join(f"- {r}" for r in parsed.get("red_flags", []))
    asha_note = parsed.get("asha_note", "")

    formatted = f"""
## {emoji} Urgency: **{urgency}**

### Possible Conditions
{conditions}

### Recommended Next Steps
{next_steps}

### Red Flag Symptoms — Watch For These
{red_flags}

### Note for ASHA Worker
{asha_note}

---
*Model: {model_used} | {datetime.now().strftime("%d %b %Y, %I:%M %p")}*
*This is triage support only — not a clinical diagnosis.*
"""
    return formatted, raw_response, None


def get_diagnosis_history_markdown(patient_dropdown):
    pid = parse_dropdown(patient_dropdown)
    if not pid:
        return "No patient selected."
    diagnoses = get_diagnoses_for_patient(pid)
    if not diagnoses:
        return "No diagnoses recorded yet for this patient."

    parts = []
    for d in diagnoses:
        emoji = URGENCY_EMOJI.get(d['urgency'], "⚪")
        parts.append(f"""
---
**{d['created_at'][:10]}** — {emoji} {d['urgency']}
**Conditions:** {d['conditions']}
**Symptoms:** {d['symptom_description']}
""")
    return "\n".join(parts)
