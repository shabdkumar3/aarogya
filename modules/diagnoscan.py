"""DiagnoScan — multimodal triage using Gemma 4."""
import base64, json, os, io
from datetime import datetime
from database.queries import save_diagnosis, get_diagnoses_for_patient, get_patient_by_id
from llm.client import call_gemma_multimodal, call_gemma_text
from llm.prompts import DIAGNOSCAN_PROMPT

IMAGE_SAVE_DIR = "saved_images"
os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)

URGENCY_EMOJI = {
    "Monitor at Home":   "🟢",
    "Visit PHC":         "🟡",
    "Emergency Referral":"🔴",
}

def _pil_to_b64(image):
    try:
        from PIL import Image
        buf = io.BytesIO()
        image.convert("RGB").save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return None

def _save_image(image):
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(IMAGE_SAVE_DIR, f"img_{ts}.jpg")
        image.convert("RGB").save(path, "JPEG")
        return path
    except Exception:
        return ""

def _parse_json(raw):
    """Try to extract JSON from raw LLM response."""
    if not raw:
        return None
    clean = raw.strip()
    # Strip markdown fences
    if "```" in clean:
        for part in clean.split("```"):
            part = part.strip().lstrip("json").strip()
            try:
                return json.loads(part)
            except Exception:
                continue
    try:
        return json.loads(clean)
    except Exception:
        pass
    # Try to find first { ... } block
    try:
        start = clean.index("{")
        end   = clean.rindex("}") + 1
        return json.loads(clean[start:end])
    except Exception:
        return None


def run_diagnoscan(pid, symptoms, image, language):
    """
    Args: pid(int), symptoms(str), image(PIL Image or None), language(str)
    Returns: (formatted_markdown: str, model_used: str)
    """
    if not pid:
        return "⚠️ No patient selected.", "—"
    if not symptoms or not str(symptoms).strip():
        return "⚠️ Please describe the symptoms.", "—"

    try:
        patient = get_patient_by_id(int(pid)) or {}
    except Exception:
        patient = {}

    image_path = ""
    raw_response = ""
    model_used = "—"

    try:
        prompt = DIAGNOSCAN_PROMPT.format(
            symptoms=str(symptoms).strip(),
            existing_conditions=patient.get("conditions") or "None",
            allergies=patient.get("allergies") or "None",
            language=language or "English",
        )

        if image is not None:
            image_path = _save_image(image)
            image_b64  = _pil_to_b64(image)
            if image_b64:
                raw_response, model_used = call_gemma_multimodal(prompt, image_b64)
            else:
                raw_response, model_used = call_gemma_text(prompt)
        else:
            raw_response, model_used = call_gemma_text(prompt)

    except Exception as e:
        raw_response = f"API error: {e}"
        model_used   = "error"

    parsed = _parse_json(raw_response)

    # Save to DB regardless of parse success
    try:
        save_diagnosis(
            patient_id=int(pid),
            image_path=image_path,
            symptom_description=str(symptoms).strip(),
            raw_response=raw_response or "",
            conditions=", ".join(parsed.get("conditions", [])) if parsed else "",
            urgency=parsed.get("urgency", "") if parsed else "",
            next_steps="; ".join(parsed.get("next_steps", [])) if parsed else "",
            red_flags="; ".join(parsed.get("red_flags", [])) if parsed else "",
            model_used=model_used,
        )
    except Exception:
        pass

    if parsed:
        urgency   = parsed.get("urgency", "Unknown")
        emoji     = URGENCY_EMOJI.get(urgency, "⚪")
        conditions= "\n".join(f"- {c}" for c in parsed.get("conditions", []))
        steps     = "\n".join(f"- {s}" for s in parsed.get("next_steps", []))
        flags     = "\n".join(f"- {r}" for r in parsed.get("red_flags", []))
        asha_note = parsed.get("asha_note", "")
        ts        = datetime.now().strftime("%d %b %Y, %I:%M %p")
        result = (
            f"## {emoji} Urgency: **{urgency}**\n\n"
            f"### Possible Conditions\n{conditions}\n\n"
            f"### Recommended Next Steps\n{steps}\n\n"
            f"### Red Flag Symptoms — Watch For\n{flags}\n\n"
            f"### ASHA Worker Note\n{asha_note}\n\n"
            f"---\n*Model: {model_used} | {ts}*\n"
            f"*Triage support only — not a clinical diagnosis.*"
        )
    else:
        result = (
            f"⚠️ Could not parse structured response.\n\n"
            f"**Raw model output:**\n\n{raw_response}\n\n"
            f"---\n*Model: {model_used}*"
        )

    return result, model_used


def get_diagnosis_history_markdown(pid):
    """Returns markdown history for a patient. pid is int."""
    if not pid:
        return "*No patient selected.*"
    try:
        diagnoses = get_diagnoses_for_patient(int(pid))
    except Exception:
        return "*Error loading history.*"
    if not diagnoses:
        return "*No diagnoses recorded yet.*"
    parts = []
    for d in diagnoses[:10]:
        emoji = URGENCY_EMOJI.get(d.get('urgency', ''), "⚪")
        parts.append(
            f"**{str(d.get('created_at',''))[:10]}** — {emoji} {d.get('urgency','')}\n"
            f"Conditions: {d.get('conditions','')}\n"
            f"Symptoms: {d.get('symptom_description','')[:120]}"
        )
    return "\n\n---\n\n".join(parts)
