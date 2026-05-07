"""
Aarogya LLM Client — 100 % Gemma family.

  • Primary cloud: Google AI Studio  →  gemma-4-27b-it / gemma-3-27b-it / gemma-3-12b-it
  • Edge / offline: Ollama           →  gemma4:4b or gemma2:9b

Includes:
  - Auto-fallback chain across Gemma sizes (Gemma 4 if available, else Gemma 3)
  - Exponential backoff on HTTP 429 (rate limit) and 5xx
  - Native function-calling (Gemini tool-use API)
  - Multimodal (image + text)
  - Offline-stub responses so demo never fully crashes
"""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODEL_MODE", "api")
GOOGLE_API_KEY  = os.getenv("GOOGLE_API_KEY", "").strip()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "gemma2:9b")

# Gemma fallback chain — Gemma 4 first, gracefully degrade to Gemma 3
# (No Flash / non-Gemma fallback — hackathon requires Gemma)
GEMMA_FALLBACK = [
    os.getenv("GEMMA_MODEL", "gemma-4-31b-it"),
    "gemma-4-26b-a4b-it",
]

# Cache resolved models per call type so we don't re-probe every request
_RESOLVED = {"text": None, "multimodal": None, "tools": None}


# ═══════════════════════════════════════════════════════════
# Low-level Gemini REST helper with retries
# ═══════════════════════════════════════════════════════════
def _api_url(model):
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _post(model, payload, timeout=90):
    return requests.post(
        _api_url(model),
        headers={"Content-Type": "application/json"},
        params={"key": GOOGLE_API_KEY},
        json=payload,
        timeout=timeout,
    )


def _post_with_backoff(model, payload, max_retries=4, timeout=90):
    """POST with exponential backoff on 429/5xx. Returns Response or raises."""
    delay = 2.0
    last_err = None
    for attempt in range(max_retries):
        try:
            r = _post(model, payload, timeout=timeout)
            if r.status_code in (429, 500, 502, 503, 504):
                last_err = f"{r.status_code} {r.text[:120]}"
                time.sleep(delay)
                delay *= 2
                continue
            r.raise_for_status()
            return r
        except requests.HTTPError as e:
            last_err = e
            if e.response is not None and e.response.status_code in (429, 500, 502, 503, 504):
                time.sleep(delay)
                delay *= 2
                continue
            raise
        except requests.RequestException as e:
            last_err = e
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(f"Gemma request failed after {max_retries} retries: {last_err}")


def _resolve(call_type, payload):
    """Probe fallback chain once per call_type; cache the winner."""
    cached = _RESOLVED.get(call_type)
    if cached:
        try:
            r = _post_with_backoff(cached, payload)
            return cached, r
        except Exception:
            _RESOLVED[call_type] = None  # invalidate

    last_err = None
    for model in GEMMA_FALLBACK:
        try:
            r = _post_with_backoff(model, payload, max_retries=2)
            _RESOLVED[call_type] = model
            print(f"[Aarogya] Resolved Gemma model for {call_type}: {model}")
            return model, r
        except requests.HTTPError as e:
            last_err = e
            if e.response is not None and e.response.status_code == 404:
                continue
            raise
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"No usable Gemma model on this API key. Last error: {last_err}")


def _extract_text(resp_json):
    try:
        return resp_json["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return None


# ═══════════════════════════════════════════════════════════
# TEXT
# ═══════════════════════════════════════════════════════════
def call_gemma_text(prompt, temperature=0.3, max_tokens=1024):
    if MODE == "ollama":
        return _ollama_text(prompt), f"ollama-{OLLAMA_MODEL}"

    if not GOOGLE_API_KEY:
        return _offline_stub(prompt), "offline-stub"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    try:
        model, r = _resolve("text", payload)
        text = _extract_text(r.json()) or "No response generated."
        return text, f"gemma-api-{model}"
    except Exception as e:
        print(f"[GEMMA TEXT ERROR] {e}")
        return _offline_stub(prompt, error=str(e)), "gemma-error"


# ═══════════════════════════════════════════════════════════
# MULTIMODAL  (image + text)
# ═══════════════════════════════════════════════════════════
def call_gemma_multimodal(prompt, image_b64, temperature=0.2, max_tokens=1024):
    if MODE == "ollama":
        return _ollama_multimodal(prompt, image_b64), f"ollama-{OLLAMA_MODEL}"

    if not GOOGLE_API_KEY:
        return _offline_stub(prompt, multimodal=True), "offline-stub"

    payload = {
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": "image/jpeg", "data": image_b64}},
                {"text": prompt},
            ]
        }],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    try:
        model, r = _resolve("multimodal", payload)
        text = _extract_text(r.json()) or "No response generated."
        return text, f"gemma-api-{model}"
    except Exception as e:
        print(f"[GEMMA MULTIMODAL ERROR] {e}")
        return _offline_stub(prompt, multimodal=True, error=str(e)), "gemma-error"


# ═══════════════════════════════════════════════════════════
# FUNCTION CALLING (Gemini native tool-use)
# ═══════════════════════════════════════════════════════════
def call_gemma_with_tools(prompt, tools, temperature=0.3, max_tokens=1024):
    from llm.tools import execute_tool

    if MODE == "ollama":
        return _ollama_text(prompt + "\n\nGenerate a detailed follow-up note."), f"ollama-{OLLAMA_MODEL}-nofuncall"

    if not GOOGLE_API_KEY:
        return _offline_stub(prompt, funcall=True), "offline-stub"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"function_declarations": tools}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    try:
        model, r = _resolve("tools", payload)
        data = r.json()
        candidate = data["candidates"][0]["content"]
        parts = candidate.get("parts", [])

        tool_results = []
        for part in parts:
            if "functionCall" in part:
                fname = part["functionCall"]["name"]
                fargs = part["functionCall"].get("args", {})
                result = execute_tool(fname, fargs)
                tool_results.append({
                    "functionResponse": {"name": fname, "response": {"result": result}}
                })

        if not tool_results:
            return parts[0].get("text", "No analysis generated."), f"gemma-api-{model}"

        # Round 2 — feed tool results back
        messages = [
            {"role": "user", "parts": [{"text": prompt}]},
            {"role": "model", "parts": parts},
            {"role": "user", "parts": tool_results},
        ]
        payload2 = {
            "contents": messages,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        }
        r2 = _post_with_backoff(model, payload2)
        text = _extract_text(r2.json()) or "No analysis generated."
        return text, f"gemma-api-{model}-funcall"

    except Exception as e:
        print(f"[GEMMA FUNCTION CALLING ERROR] {e}")
        return _offline_stub(prompt, funcall=True, error=str(e)), "gemma-error"


# ═══════════════════════════════════════════════════════════
# OLLAMA  (offline / edge)
# ═══════════════════════════════════════════════════════════
def _ollama_text(prompt):
    try:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=120,
        )
        return r.json().get("response", "Ollama returned no response.")
    except Exception as e:
        return f"Ollama unreachable: {e}\n\nRun: ollama pull {OLLAMA_MODEL} && ollama serve"


def _ollama_multimodal(prompt, image_b64):
    try:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "images": [image_b64], "stream": False},
            timeout=180,
        )
        return r.json().get("response", "Ollama returned no response.")
    except Exception as e:
        return f"Ollama unreachable: {e}"


# ═══════════════════════════════════════════════════════════
# OFFLINE STUB
# ═══════════════════════════════════════════════════════════
def _offline_stub(prompt, multimodal=False, funcall=False, error=None):
    header = "⚠️ **Aarogya is in offline-stub mode** (no API key set or Gemma unavailable)."
    if error:
        header += f"\n\n_Last error: {str(error)[:240]}_"
    if multimodal:
        body = (
            "\n\n**Suggested triage (stub):**\n"
            "- **Likely:** common viral / seasonal infection or local skin irritation\n"
            "- **Risk:** Yellow — observable but not emergency\n"
            "- **Action:** Encourage rest, fluids, observe 48 hrs. If fever > 102 °F or worsening → refer to PHC.\n"
            "- **Red flags:** breathlessness, severe rash, persistent vomiting → URGENT referral."
        )
    elif funcall:
        body = (
            "\n\n**Adherence analysis (stub):**\n"
            "Patient adherence pattern suggests follow-up is needed. With a working API key, "
            "Gemma would call `get_adherence_summary`, `flag_at_risk`, `suggest_barrier`, "
            "and `generate_followup_note` to produce a structured ASHA action plan."
        )
    else:
        body = (
            "\n\nAdd `GOOGLE_API_KEY` to `.env` "
            "(get one free at https://aistudio.google.com/apikey) and restart the app."
        )
    return header + body
