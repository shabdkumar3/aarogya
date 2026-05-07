import gradio as gr
from modules.diagnoscan import run_diagnoscan, get_diagnosis_history_markdown
from database.queries import get_patient_dropdown_choices


def build_diagnoscan_tab():
    with gr.Tab("🔬  DiagnoScan"):
        gr.HTML("""
        <div class="aa-tab-title">AI Triage Assessment</div>
        <div class="aa-tab-subtitle">Upload a patient photo + describe symptoms. Gemma 4's multimodal vision returns structured triage in the patient's language.</div>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML('<div class="aa-section-label">Input</div>')
                patient_dd  = gr.Dropdown(label="Select Patient *", choices=get_patient_dropdown_choices(), interactive=True)
                refresh_btn = gr.Button("🔄  Refresh Patients", variant="secondary", size="sm")
                image_in    = gr.Image(label="📷  Photo of Condition *", type="pil", height=240)
                symptom_in  = gr.Textbox(label="Describe Symptoms *",
                                         placeholder="Hindi ya English mein likhein...\nजैसे: 3 din se bukhar hai, pair mein dard hai",
                                         lines=4)
                lang_in     = gr.Dropdown(label="Response Language",
                                          choices=["Hindi","English","Tamil","Telugu","Bengali"],
                                          value="Hindi")
                scan_btn    = gr.Button("🔍  Run DiagnoScan", variant="primary", size="lg")

            with gr.Column(scale=1):
                gr.HTML('<div class="aa-section-label">Triage Result</div>')
                result_out  = gr.Markdown("*Results will appear here after running DiagnoScan.*")
                error_out   = gr.Markdown("")
                with gr.Accordion("🛠  Raw JSON Output (debug)", open=False):
                    raw_out = gr.Textbox(label="Raw Model Output", lines=8, interactive=False)

        gr.HTML('<div class="aa-section-label" style="margin-top:32px">Diagnosis History</div>')
        history_btn = gr.Button("📋  Load History", variant="secondary")
        history_out = gr.Markdown("")

        def on_scan(patient, image, symptoms, language):
            formatted, raw, error = run_diagnoscan(patient, image, symptoms, language)
            err_display = f"❌ {error}" if error else ""
            return formatted, err_display, raw or ""

        refresh_btn.click(fn=lambda: gr.update(choices=get_patient_dropdown_choices()), outputs=patient_dd)
        scan_btn.click(fn=on_scan, inputs=[patient_dd, image_in, symptom_in, lang_in],
                       outputs=[result_out, error_out, raw_out])
        history_btn.click(fn=get_diagnosis_history_markdown, inputs=patient_dd, outputs=history_out)
