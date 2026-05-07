import gradio as gr
from modules.patient_lite import run_patient_lite_text
from modules.voice import transcribe_audio, text_to_audio


def build_patient_lite_tab():
    with gr.Tab("🧑‍🌾  Patient Self-Check"):
        gr.HTML("""
        <div class="aa-tab-title">Patient Self-Check <span style="color:#64748b;font-weight:500">/ मरीज़ स्व-जांच</span></div>
        <div class="aa-tab-subtitle">No registration needed · Your information is not saved · Works in 5 Indian languages.</div>
        <div class="aa-callout aa-callout-warning">
          ⚠️ <strong>यह tool डॉक्टर की जगह नहीं लेता।</strong> गंभीर बीमारी में डॉक्टर से मिलें।
          &nbsp;|&nbsp; This tool does not replace a doctor. For serious conditions, see a doctor immediately.
        </div>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                lang_in    = gr.Radio(label="Language / भाषा",
                                      choices=["Hindi","English","Tamil","Telugu","Bengali"],
                                      value="Hindi")
                symptom_in = gr.Textbox(label="Apne lakshan likhein / Describe your symptoms",
                                        placeholder="जैसे: 3 दिन से बुखार है और सिर दर्द है\ne.g. Fever for 3 days with headache",
                                        lines=5)
                image_in   = gr.Image(label="📷  Photo (optional — upload if there's a visible condition)",
                                      type="pil", height=180)
                submit_btn = gr.Button("🩺  Get Guidance / Salah Lein", variant="primary", size="lg")

                with gr.Accordion("🎤  Voice Input — Bol ke Batayein", open=False):
                    gr.HTML('<div style="font-size:0.8rem;color:#64748b;margin-bottom:8px">Record your symptoms instead of typing</div>')
                    audio_in       = gr.Audio(label="Record Symptoms", type="filepath", sources=["microphone"])
                    transcribe_btn = gr.Button("🔄  Convert Voice to Text", variant="secondary")
                    transcribe_status = gr.Markdown("")

            with gr.Column(scale=1):
                gr.HTML('<div class="aa-section-label">Guidance / सलाह</div>')
                response_out = gr.Textbox(label="", lines=12, interactive=False,
                                          placeholder="Your guidance will appear here after clicking Get Guidance...\nसलाह यहाँ दिखेगी...")
                error_out = gr.Markdown("")

                gr.HTML('<div class="aa-section-label" style="margin-top:24px">Audio Response</div>')
                speak_btn   = gr.Button("🔊  Read Response Aloud", variant="secondary")
                audio_out   = gr.Audio(label="Listen", interactive=False)
                audio_error = gr.Markdown("")

        def on_submit(symptoms, language, image):
            response, error = run_patient_lite_text(symptoms, language, image)
            if error:
                return "", f"❌ {error}"
            return response, ""

        def on_transcribe(audio_path, language):
            if not audio_path:
                return gr.update(), "❌ Please record audio first."
            text, error = transcribe_audio(audio_path, language)
            if error:
                return gr.update(), f"❌ {error}"
            return gr.update(value=text), "✅ Transcribed. Review and click Get Guidance."

        def on_speak(text, language):
            if not text or not text.strip():
                return None, "❌ No response to read. Get guidance first."
            audio_path, error = text_to_audio(text, language)
            if error:
                return None, f"❌ {error}"
            return audio_path, ""

        submit_btn.click(fn=on_submit, inputs=[symptom_in, lang_in, image_in], outputs=[response_out, error_out])
        transcribe_btn.click(fn=on_transcribe, inputs=[audio_in, lang_in], outputs=[symptom_in, transcribe_status])
        speak_btn.click(fn=on_speak, inputs=[response_out, lang_in], outputs=[audio_out, audio_error])
