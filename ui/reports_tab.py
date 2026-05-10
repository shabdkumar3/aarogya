import gradio as gr
from modules.reports import generate_patient_pdf
from database.queries import get_patient_dropdown_choices, parse_dropdown


def build_reports_tab():
    with gr.TabItem("📄 PDF Reports"):
        gr.HTML('<div class="section-header"><div class="section-icon">📄</div><h3>Generate Patient Health Reports</h3></div>')

        with gr.Row():
            with gr.Column(scale=1):
                patient_dd  = gr.Dropdown(label="Select Patient", choices=[], interactive=True)
                refresh_btn = gr.Button("🔄 Refresh", variant="secondary", size="sm")
                gen_btn     = gr.Button("📄 Generate PDF Report", variant="primary")
                status_out  = gr.Markdown(value="*Select a patient and generate their report.*")

            with gr.Column(scale=1):
                pdf_out = gr.File(label="Download Report (PDF)", interactive=False)

        def do_refresh():
            return gr.update(choices=get_patient_dropdown_choices(), value=None)

        def do_generate(selection):
            pid = parse_dropdown(selection)
            if not pid:
                return "⚠️ Please select a patient first.", None
            path, msg = generate_patient_pdf(pid)
            return msg, path

        refresh_btn.click(do_refresh, outputs=[patient_dd])
        gen_btn.click(do_generate, inputs=[patient_dd], outputs=[status_out, pdf_out])
