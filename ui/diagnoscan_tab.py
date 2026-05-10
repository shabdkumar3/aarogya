import gradio as gr
from modules.diagnoscan import run_diagnoscan, get_diagnosis_history_markdown
from database.queries import get_patient_dropdown_choices


def build_diagnoscan_tab():
    with gr.TabItem("🔬 DiagnoScan"):
        gr.HTML('<div class="section-header"><div class="section-icon">🔬</div><h3>AI-Assisted Symptom Triage</h3></div>')
        gr.HTML('<div class="alert-warning">Gemma 4 multimodal triage — for ASHA worker decision support only. Not a clinical diagnosis.</div>')

        with gr.Row():
            with gr.Column(scale=1):
                patient_dd  = gr.Dropdown(label="Select Patient", choices=[], interactive=True)
                refresh_btn = gr.Button("🔄 Refresh", variant="secondary", size="sm")
                symptoms_in = gr.Textbox(label="Describe Symptoms",
                                         placeholder="e.g. 3-day fever, cough, fatigue in child aged 7",
                                         lines=4)
                image_in    = gr.Image(label="Upload Photo (optional — skin, wound, rash)",
                                       type="pil", sources=["upload", "webcam"])
                lang_in     = gr.Dropdown(label="Response Language",
                                          choices=["Hindi", "English", "Tamil", "Telugu", "Bengali"],
                                          value="Hindi")
                scan_btn    = gr.Button("Run DiagnoScan", variant="primary")

            with gr.Column(scale=1):
                result_out  = gr.Markdown(label="Triage Report", value="*Submit symptoms to generate triage report.*")
                model_badge = gr.Textbox(label="Model Used", interactive=False, value="—")
                gr.HTML('<div style="margin-top:16px;color:#94A3B8;font-size:0.8rem;font-weight:600;">DIAGNOSIS HISTORY</div>')
                history_out = gr.Markdown(value="*Select a patient to view history.*")

        def do_scan(pid_label, symptoms, image, lang):
            if not pid_label:
                return "⚠️ Please select a patient first.", "—", ""
            try:
                pid = int(pid_label.split("|")[0].strip())
            except Exception:
                return "⚠️ Invalid patient selection.", "—", ""
            result, model = run_diagnoscan(pid, symptoms, image, lang)
            history = get_diagnosis_history_markdown(pid)
            return result, model, history

        def do_refresh():
            return gr.update(choices=get_patient_dropdown_choices())

        def load_history(pid_label):
            if not pid_label:
                return "*Select a patient to view history.*"
            try:
                pid = int(pid_label.split("|")[0].strip())
                return get_diagnosis_history_markdown(pid)
            except Exception:
                return "*Could not load history.*"

        scan_btn.click(do_scan,
                       inputs=[patient_dd, symptoms_in, image_in, lang_in],
                       outputs=[result_out, model_badge, history_out])
        refresh_btn.click(do_refresh, outputs=[patient_dd])
        patient_dd.change(load_history, inputs=[patient_dd], outputs=[history_out])
