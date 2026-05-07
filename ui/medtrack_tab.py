import gradio as gr
from modules.medtrack import (add_med, stop_med, get_active_meds_display,
                               log_dose, get_adherence_table, run_adherence_analysis, FREQUENCIES)
from database.queries import get_patient_dropdown_choices


def build_medtrack_tab():
    with gr.Tab("💊  MedTrack"):
        gr.HTML("""
        <div class="aa-tab-title">Medication Management &amp; Adherence Tracking</div>
        <div class="aa-tab-subtitle">Track daily medications and use Gemma 4 native function calling to identify at-risk patients automatically.</div>
        """)

        with gr.Row():
            patient_dd  = gr.Dropdown(label="Select Patient", choices=get_patient_dropdown_choices(), interactive=True, scale=5)
            refresh_btn = gr.Button("🔄  Refresh", scale=1, variant="secondary")

        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML('<div class="aa-section-label">Add Medication</div>')
                med_name  = gr.Textbox(label="Medication Name *", placeholder="e.g. Metformin")
                med_dose  = gr.Textbox(label="Dose *", placeholder="e.g. 500mg")
                med_freq  = gr.Dropdown(label="Frequency *", choices=FREQUENCIES, value="Once daily")
                med_start = gr.Textbox(label="Start Date * (YYYY-MM-DD)", placeholder="2026-05-01")
                med_end   = gr.Textbox(label="End Date (optional)", placeholder="Leave blank if ongoing")
                add_btn   = gr.Button("➕  Add Medication", variant="primary")
                add_status = gr.Markdown("")

                gr.HTML('<div class="aa-section-label" style="margin-top:24px">Stop Medication</div>')
                stop_id  = gr.Number(label="Medication ID to Stop", precision=0)
                stop_btn = gr.Button("🛑  Mark as Completed", variant="stop")
                stop_status = gr.Markdown("")

            with gr.Column(scale=1):
                gr.HTML('<div class="aa-section-label">Active Medications</div>')
                meds_load_btn = gr.Button("📋  Load Active Medications", variant="secondary")
                meds_display  = gr.Markdown("")

                gr.HTML('<div class="aa-section-label" style="margin-top:24px">Log Today\'s Adherence</div>')
                log_id        = gr.Number(label="Medication ID", precision=0)
                log_status_in = gr.Radio(label="Status", choices=["Took","Missed","Skipped"], value="Took")
                log_btn       = gr.Button("✅  Log Adherence", variant="primary")
                log_status_out = gr.Markdown("")

        gr.HTML('<div class="aa-section-label" style="margin-top:32px">7-Day Adherence Summary</div>')
        summary_btn = gr.Button("📅  Load Summary", variant="secondary")
        summary_out = gr.Markdown("")

        gr.HTML("""
        <div class="aa-section-label" style="margin-top:32px">Gemma 4 Adherence Analysis</div>
        <div class="aa-callout aa-callout-info">
          <strong>Native function calling.</strong> Gemma 4 autonomously chains four tools:
          <code>get_adherence_summary</code>
          <code>flag_at_risk</code>
          <code>suggest_barrier</code>
          <code>generate_followup_note</code>
        </div>
        """)
        analyze_btn  = gr.Button("🤖  Run Gemma 4 Analysis", variant="primary", size="lg")
        analysis_out = gr.Markdown("")

        refresh_btn.click(fn=lambda: gr.update(choices=get_patient_dropdown_choices()), outputs=patient_dd)
        add_btn.click(fn=add_med, inputs=[patient_dd,med_name,med_dose,med_freq,med_start,med_end], outputs=add_status)
        stop_btn.click(fn=stop_med, inputs=stop_id, outputs=stop_status)
        meds_load_btn.click(fn=get_active_meds_display, inputs=patient_dd, outputs=meds_display)
        log_btn.click(fn=log_dose, inputs=[patient_dd,log_id,log_status_in], outputs=log_status_out)
        summary_btn.click(fn=get_adherence_table, inputs=patient_dd, outputs=summary_out)
        analyze_btn.click(fn=run_adherence_analysis, inputs=patient_dd, outputs=analysis_out)
