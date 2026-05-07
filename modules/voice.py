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


def transcribe_audio(audio_path: str, language: str = "Hindi"):
    try:
        import whisper
    except ImportError:
        return "", "Whisper not installed. Run: pip install openai-whisper"

    lang_code = WHISPER_LANG_CODES.get(language, "hi")
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language=lang_code)
        text = result.get("text", "").strip()
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
