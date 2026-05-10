"""Patient Lite — simple Q&A for low-literacy rural patients."""
import base64, io
from llm.client import call_gemma_multimodal, call_gemma_text
from llm.prompts import PATIENT_LITE_PROMPT


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
                answer, model = call_gemma_multimodal(prompt, image_b64)
            except Exception:
                answer, model = call_gemma_text(prompt)
        else:
            answer, model = call_gemma_text(prompt)

        return (answer or "No response received."), (model or "—")

    except Exception as e:
        return f"❌ Could not get a response: {e}", "error"
