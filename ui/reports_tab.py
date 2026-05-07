import gradio as gr
from modules.reports import generate_patient_pdf
from database.queries import get_patient_dropdown_choices


def build_reports_tab():
    with gr.Tab("📄  PDF Reports"):
        gr.HTML("""
        <div class="aa-tab-title">Generate Patient Health Report</div>
        <div class="aa-tab-subtitle">Creates a printable PDF summary for handing to a PHC doctor — includes AI-written clinical summary.</div>
        """)

        with gr.Row():
            patient_dd  = gr.Dropdown(label="Select Patient", choices=get_patient_dropdown_choices(), interactive=True, scale=5)
            refresh_btn = gr.Button("🔄  Refresh", scale=1, variant="secondary")

        gr.HTML("""
        <div class="aa-callout aa-callout-success" style="margin-top:14px">
          📋 <strong>The PDF includes:</strong> patient profile · recent triage assessments · active medications · 7-day adherence log · AI-generated clinical summary (English).
        </div>
        """)

        generate_btn = gr.Button("📄  Generate PDF Report", variant="primary", size="lg")
        status_out   = gr.Markdown("")
        pdf_out      = gr.File(label="Download Report", visible=False)

        def on_generate(patient_dropdown):
            pdf_path, error = generate_patient_pdf(patient_dropdown)
            if error:
                return f"❌ {error}", gr.update(visible=False)
            return "✅ Report generated successfully. Click below to download.", gr.update(value=pdf_path, visible=True)

        refresh_btn.click(fn=lambda: gr.update(choices=get_patient_dropdown_choices()), outputs=patient_dd)
        generate_btn.click(fn=on_generate, inputs=patient_dd, outputs=[status_out, pdf_out])
