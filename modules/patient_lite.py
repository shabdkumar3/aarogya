import base64
import io
from PIL import Image
from llm.client import call_gemma_multimodal, call_gemma_text
from llm.prompts import PATIENT_LITE_PROMPT


def run_patient_lite_text(symptom_text, language, image=None):
    if not symptom_text or not symptom_text.strip():
        return None, "Please describe your symptoms."

    prompt = PATIENT_LITE_PROMPT.format(
        symptoms=symptom_text.strip(),
        language=language
    )

    if image is not None:
        buf = io.BytesIO()
        image.convert("RGB").save(buf, format="JPEG", quality=85)
        image_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        response, _ = call_gemma_multimodal(prompt, image_b64)
    else:
        response, _ = call_gemma_text(prompt)

    if response is None:
        return None, "Could not get a response. Please check your connection."
    return response, None
