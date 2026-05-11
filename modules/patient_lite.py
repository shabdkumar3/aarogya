"""Patient Lite — simple Q&A for low-literacy rural patients."""
import base64, io, re
from llm.client import call_gemma_multimodal, call_gemma_text
from llm.prompts import PATIENT_LITE_PROMPT


def _clean_response(text):
    """
    Strip Gemma 4 chain-of-thought scaffolding.
    The model sometimes outputs reasoning bullets/headers before the actual answer.
    We want only the final clean conversational paragraph(s).
    """
    if not text:
        return text

    # If the response contains the actual Hindi/vernacular answer after reasoning,
    # extract the last clean quoted block (wrapped in " or just the last paragraph cluster)
    # Look for a final "draft" block between quotes
    quoted = re.findall(r'"([^"]{30,})"', text, re.DOTALL)
    if quoted:
        return quoted[-1].strip()

    # Strip lines that look like reasoning scaffolding:
    # - Lines starting with *, -, •, numbered lists with reasoning labels
    # - Lines containing "Draft:", "Cause:", "Immediate Actions:", "Emergency Sign:"
    # - Lines containing "Hindi:", "Yes.", "Yes ("
    # - Lines with nested bullets (multiple spaces + * or -)
    JUNK_PATTERNS = [
        r'^\s*\*\s+\*[\w]',          # * *Label:*
        r'^\s*[-*•]\s+\*\*(Draft|Cause|Immediate|Emergency|Hindi)',
        r'^\s*[-*•]\s+(Draft|Cause|Immediate Actions|Emergency Sign|Hindi):',
        r'^\s*\d+[-.)]\s+\*\*',      # 1. **something
        r'^\s*\*\s+\d+[-.)]\s',      # *   1. something
        r'^\s*[-*•]\s+\*[\w]',       # * *something*
        r'(Likely cause|1-2 sentences|2-3 immediate|under 80 words|'
        r'No JSON|No bullet|conversational Hindi|Under 80)',
    ]

    lines = text.splitlines()
    clean_lines = []
    for line in lines:
        skip = False
        for pat in JUNK_PATTERNS:
            if re.search(pat, line, re.IGNORECASE):
                skip = True
                break
        if not skip:
            clean_lines.append(line)

    cleaned = "\n".join(clean_lines).strip()

    # If still looks like it has markdown reasoning, take last solid paragraph block
    if re.search(r'(\*{1,2}[A-Z]|\d\.\s+\*)', cleaned):
        # Split on double newlines and take last non-empty chunk
        paragraphs = [p.strip() for p in re.split(r'\n{2,}', cleaned) if p.strip()]
        if paragraphs:
            # Prefer the last paragraph that doesn't start with * or - or digit
            for para in reversed(paragraphs):
                if not re.match(r'^[\*\-\d]', para):
                    return para
            return paragraphs[-1]

    return cleaned if cleaned else text.strip()


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

        answer = _clean_response(raw) or "No response received."
        return answer, (model or "—")

    except Exception as e:
        return f"❌ Could not get a response: {e}", "error"
