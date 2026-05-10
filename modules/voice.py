"""
Voice Pipeline for Patient Lite Mode.
STT: OpenAI Whisper (local, offline)
TTS: gTTS — requires internet. Falls back gracefully if offline.
"""
import os
import tempfile

WHISPER_LANG_CODES = {
    "Hindi": "hi", "English": "en", "Tamil": "ta", "Telugu": "te", "Bengali": "bn"
}
GTTS_LANG_CODES = {
    "Hindi": "hi", "English": "en", "Tamil": "ta", "Telugu": "te", "Bengali": "bn"
}


_FW_MODEL = None


def _get_whisper_model():
    """Lazy-load faster-whisper (CTranslate2-based, works on Python 3.11+)."""
    global _FW_MODEL
    if _FW_MODEL is not None:
        return _FW_MODEL
    from faster_whisper import WhisperModel
    _FW_MODEL = WhisperModel("base", device="cpu", compute_type="int8")
    return _FW_MODEL


def transcribe_audio(audio_path: str, language: str = "Hindi"):
    try:
        model = _get_whisper_model()
    except ImportError:
        return "", "faster-whisper not installed. Run: pip install faster-whisper"
    except Exception as e:
        return "", f"Whisper model load failed: {e}"

    lang_code = WHISPER_LANG_CODES.get(language, "hi")
    try:
        segments, _info = model.transcribe(audio_path, language=lang_code, beam_size=1)
        text = " ".join(seg.text for seg in segments).strip()
        if not text:
            return "", "Could not understand the audio. Please try speaking more clearly."
        return text, None
    except Exception as e:
        return "", f"Transcription error: {str(e)}"


def text_to_audio(text: str, language: str = "Hindi"):
    try:
        from gtts import gTTS
    except ImportError:
        return None, "gTTS not installed. Run: pip install gTTS"

    lang_code = GTTS_LANG_CODES.get(language, "hi")
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tts.save(tmp.name)
        return tmp.name, None
    except Exception as e:
        return None, f"Audio generation failed (requires internet): {str(e)}"
