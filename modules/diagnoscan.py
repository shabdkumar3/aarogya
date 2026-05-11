"""DiagnoScan — multimodal triage using Gemma 4."""
import base64, json, os, io, re
from datetime import datetime
from database.queries import save_diagnosis, get_diagnoses_for_patient, get_patient_by_id
from llm.client import call_gemma_multimodal, call_gemma_text
from llm.prompts import DIAGNOSCAN_PROMPT

IMAGE_SAVE_DIR = "saved_images"
os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)

URGENCY_EMOJI = {
    "Monitor at Home":    "🟢",
    "Visit PHC":          "🟡",
    "Emergency Referral": "🔴",
}

VALID_URGENCIES = {"Monitor at Home", "Visit PHC", "Emergency Referral"}


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
    """
    Aggressively extract a triage JSON from raw LLM text.
    Handles: pure JSON, markdown fences, reasoning-then-JSON,
    and partial/malformed JSON with fixable urgency values.
    """
    if not raw:
        return None
    text = raw.strip()

    # 1. Strip markdown fences
    if "```" in text:
        parts = text.split("```")
        candidates = [p.strip().lstrip("json").strip() for p in parts]
    else:
        candidates = [text]

    # 2. For each candidate try direct parse, then brace extraction
    for cand in candidates:
        # Direct parse
        try:
            obj = json.loads(cand)
            if isinstance(obj, dict) and "urgency" in obj:
                return _normalise(obj)
        except Exception:
            pass
        # Find outermost { ... }
        try:
            start = cand.index("{")
            end   = cand.rindex("}") + 1
            obj = json.loads(cand[start:end])
            if isinstance(obj, dict) and "urgency" in obj:
                return _normalise(obj)
        except Exception:
            pass

    # 3. Scan ALL { ... } blocks in the full raw text (handles reasoning-then-JSON)
    for m in re.finditer(r'\{[^{}]*"urgency"[^{}]*\}', text, re.DOTALL):
        try:
            obj = json.loads(m.group())
            return _normalise(obj)
        except Exception:
            pass

    # 4. Greedy scan — largest { ... } block that parses
    try:
        start = text.index("{")
        end   = text.rindex("}") + 1
        obj = json.loads(text[start:end])
        if isinstance(obj, dict):
            return _normalise(obj)
    except Exception:
        pass

    # 5. Build fallback JSON from free-text reasoning
    return _build_from_text(text)


def _normalise(obj):
    """Coerce urgency to exact enum value."""
    u = str(obj.get("urgency", "")).strip()
    u_low = u.lower()
    if "emergency" in u_low or "referral" in u_low:
        obj["urgency"] = "Emergency Referral"
    elif "phc" in u_low or "visit" in u_low or "clinic" in u_low or "doctor" in u_low:
        obj["urgency"] = "Visit PHC"
    elif "monitor" in u_low or "home" in u_low or "watch" in u_low:
        obj["urgency"] = "Monitor at Home"
    # Ensure required keys exist
    obj.setdefault("conditions", ["Unspecified condition"])
    obj.setdefault("next_steps", ["Seek medical advice"])
    obj.setdefault("red_flags",  ["High fever", "Difficulty breathing"])
    obj.setdefault("asha_note",  "Monitor patient and follow up in 24 hours.")
    if obj["urgency"] not in VALID_URGENCIES:
        obj["urgency"] = "Visit PHC"
    return obj


def _build_from_text(text):
    """Last-resort: infer urgency from keywords and wrap raw text as best-effort JSON."""
    t = text.lower()
    if any(k in t for k in ["emergency", "immediately", "life-threatening", "ambulance",
                              "icu", "severe", "unconscious", "seizure", "urgent referral"]):
        urgency = "Emergency Referral"
    elif any(k in t for k in ["phc", "clinic", "doctor", "physician", "hospital",
                               "test", "blood", "scan", "consult", "visit"]):
        urgency = "Visit PHC"
    else:
        urgency = "Monitor at Home"

    # Try to pull condition names from lines mentioning "condition", "diagnosis", "likely"
    conditions = []
    for line in text.splitlines():
        ll = line.lower()
        if any(k in ll for k in ["leptospirosis", "malaria", "dengue", "typhoid",
                                   "pneumonia", "dehydration", "anaemia", "anemia",
                                   "diarrhoea", "diarrhea", "fever", "infection",
                                   "conditions:", "likely:", "diagnosis:"]):
            cline = re.sub(r'^[\-\*\d\.\s]+', '', line).strip()
            if 5 < len(cline) < 80:
                conditions.append(cline)
        if len(conditions) >= 3:
            break

    if not conditions:
        conditions = ["Possible infection — see full model response below"]

    return {
        "conditions":  conditions[:3],
        "urgency":     urgency,
        "next_steps":  ["Review full model response for detailed guidance",
                        "Monitor patient vitals", "Contact PHC if symptoms worsen"],
        "red_flags":   ["High fever above 102°F", "Difficulty breathing or altered consciousness"],
        "asha_note":   "Full model reasoning shown below. Use clinical judgment.",
        "_raw":        text[:600],   # stash for debug display
    }


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

    image_path   = ""
    raw_response = ""
    model_used   = "—"

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

    # Save to DB
    try:
        save_diagnosis(
            patient_id=int(pid),
            image_path=image_path,
            symptom_description=str(symptoms).strip(),
            raw_response=raw_response or "",
            conditions=", ".join(parsed.get("conditions", [])) if parsed else "",
            urgency=parsed.get("urgency", "")    if parsed else "",
            next_steps="; ".join(parsed.get("next_steps", [])) if parsed else "",
            red_flags="; ".join(parsed.get("red_flags", []))   if parsed else "",
            model_used=model_used,
        )
    except Exception:
        pass

    if parsed:
        urgency    = parsed.get("urgency", "Unknown")
        emoji      = URGENCY_EMOJI.get(urgency, "⚪")
        conditions = "\n".join(f"- {c}" for c in parsed.get("conditions", []))
        steps      = "\n".join(f"- {s}" for s in parsed.get("next_steps", []))
        flags      = "\n".join(f"- {r}" for r in parsed.get("red_flags", []))
        asha_note  = parsed.get("asha_note", "")
        ts         = datetime.now().strftime("%d %b %Y, %I:%M %p")

        # If we fell back to text-extraction, show the raw model reasoning too
        raw_section = ""
        if "_raw" in parsed:
            raw_section = (
                f"\n\n---\n<details><summary>📄 Full model reasoning</summary>\n\n"
                f"{parsed['_raw']}\n</details>"
            )

        result = (
            f"## {emoji} Urgency: **{urgency}**\n\n"
            f"### Possible Conditions\n{conditions}\n\n"
            f"### Recommended Next Steps\n{steps}\n\n"
            f"### Red Flag Symptoms — Watch For\n{flags}\n\n"
            f"### ASHA Worker Note\n{asha_note}"
            f"{raw_section}\n\n"
            f"---\n*Model: {model_used} | {ts}*\n"
            f"*Triage support only — not a clinical diagnosis.*"
        )
    else:
        result = (
            f"⚠️ Could not parse response. Raw model output:\n\n{raw_response}\n\n"
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
        emoji = URGENCY_EMOJI.get(d.get("urgency", ""), "⚪")
        parts.append(
            f"**{str(d.get('created_at',''))[:10]}** — {emoji} {d.get('urgency','')}\n"
            f"Conditions: {d.get('conditions','')}\n"
            f"Symptoms: {d.get('symptom_description','')[:120]}"
        )
    return "\n\n---\n\n".join(parts)
