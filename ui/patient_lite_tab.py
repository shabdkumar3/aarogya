import gradio as gr
from modules.patient_lite import run_patient_lite_text
from modules.voice import transcribe_audio, text_to_audio


def build_patient_lite_tab():
    with gr.TabItem("🌾 Patient Lite"):
        gr.HTML('<div class="section-header"><div class="section-icon">🌾</div><h3>Low-Bandwidth Patient Interface</h3></div>')
        gr.HTML('<div class="alert-ok">Designed for patients with basic phones. Simple text Q&A in local language with optional voice output.</div>')

        with gr.Row():
            with gr.Column(scale=1):
                lang_in    = gr.Dropdown(
                    label="Language / भाषा",
                    choices=["Hindi", "English", "Tamil", "Telugu", "Bengali"],
                    value="Hindi"
                )
                text_in    = gr.Textbox(
                    label="Type your health question / अपना सवाल टाइप करें",
                    placeholder="e.g. मुझे तेज बुखार है, क्या करूँ?",
                    lines=3
                )
                audio_in   = gr.Audio(
                    label="Or record your question (voice)",
                    type="filepath", sources=["microphone"]
                )
                submit_btn = gr.Button("Get Answer / जवाब पाएं", variant="primary")

            with gr.Column(scale=1):
                answer_out  = gr.Markdown(label="Answer", value="*Ask a question to get started.*")
                audio_out   = gr.Audio(label="Listen to Answer", type="filepath", interactive=False)
                model_badge = gr.Textbox(label="Model Used", interactive=False, value="—")

        def do_submit(lang, text, audio_path):
            # STT stub — transcribe if audio provided
            if audio_path and not text.strip():
                transcribed, err = transcribe_audio(audio_path, lang)
                if transcribed:
                    text = transcribed
                elif err:
                    text = ""

            if not text.strip():
                return "⚠️ Please type your question (voice transcription not available).", None, "—"

            answer, model = run_patient_lite_text(text, lang)

            # TTS
            audio_file, tts_err = text_to_audio(answer, lang)
            if tts_err:
                audio_file = None

            return answer, audio_file, model

        submit_btn.click(
            do_submit,
            inputs=[lang_in, text_in, audio_in],
            outputs=[answer_out, audio_out, model_badge]
        )
