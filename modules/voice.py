"""
Voice Pipeline for Patient Lite Mode.
STT: Stub (faster-whisper removed — C++ deps cause HF Space build failures)
TTS: gTTS — requires internet. Falls back gracefully if offline.
"""
import tempfile

GTTS_LANG_CODES = {
    "Hindi": "hi", "English": "en", "Tamil": "ta", "Telugu": "te", "Bengali": "bn"
}


def transcribe_audio(audio_path: str, language: str = "Hindi"):
    """Voice transcription is not available — faster-whisper has been removed.
    Returns a stub message prompting the user to type instead."""
    return "", "Voice transcription not available - please type your symptoms."


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
