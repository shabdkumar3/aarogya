"""Patient Lite — simple Q&A for low-literacy rural patients."""
import base64, io, re
from llm.client import call_gemma_multimodal, call_gemma_text
from llm.prompts import PATIENT_LITE_PROMPT


def _clean_response(text):
    """
    Strip Gemma 4 chain-of-thought scaffolding.
    Only remove lines that are clearly internal reasoning — NOT the actual answer.
    """
    if not text:
        return text

    lines = text.splitlines()
    clean = []
    skip_patterns = [
        r'^\s*[-*•]\s+\*\*(Cause|Immediate|Emergency|Draft|Hindi|Language|Format)',
        r'^\s*\d+\.\s+\*\*',            # 1. **Something
        r'^\s*[-*]\s+\d+[-.)]\s',       # * 1. something
        r'(1-2 sentences|2-3 simple|under 80 words|No JSON|No bullet|conversational Hindi)',
        r'^\s*[-*•]\s+\*(Cause|Draft|Immediate|Emergency)',
        r'^\*\s+\*Cause',
        r'^#+\s',                        # ## headers
    ]

    for line in lines:
        skip = any(re.search(p, line, re.IGNORECASE) for p in skip_patterns)
        if not skip:
            clean.append(line)

    result = '\n'.join(clean).strip()

    # If still has heavy markdown reasoning, take last solid paragraph
    if re.search(r'(\*{2}[A-Z]|\n\s*[-*]\s)', result):
        paragraphs = [p.strip() for p in re.split(r'\n{2,}', result) if p.strip()]
        # Find last paragraph that looks like a real sentence (not a bullet list)
        for para in reversed(paragraphs):
            if not re.match(r'^[\*\-\d#]', para) and len(para) > 30:
                return para

    return result if result else text.strip()


def run_patient_lite_text(symptom_text, language, image=None):
    """
    Args: symptom_text(str), language(str), image(PIL Image or None)
    Returns: (answer_str, model_str)
    """
    if not symptom_text or not str(symptom_text).strip():
        return "⚠️ Please describe your symptoms.", "—"

    try:
        prompt = PATIENT_LITE_PROMPT.format(
            symptoms=str(symptom_text).strip(),
            language=language or "Hindi",
        )

        if image is not None:
            try:
                buf = io.BytesIO()
                image.convert("RGB").save(buf, format="JPEG", quality=85)
                image_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                raw, model = call_gemma_multimodal(prompt, image_b64)
            except Exception:
                raw, model = call_gemma_text(prompt)
        else:
            raw, model = call_gemma_text(prompt)

        answer = _clean_response(raw) or raw or "No response received."
        return answer, (model or "—")

    except Exception as e:
        return f"❌ Error: {e}", "error"
