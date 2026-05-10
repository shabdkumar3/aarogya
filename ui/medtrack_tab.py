import gradio as gr
from modules.medtrack import (add_med, stop_med, get_active_meds_display,
                               log_dose, get_adherence_table, run_adherence_analysis, FREQUENCIES)
from database.queries import get_patient_dropdown_choices


def build_medtrack_tab():
    with gr.TabItem("💊 MedTrack"):
        gr.HTML('<div class="section-header"><div class="section-icon">💊</div><h3>Medication Tracking & Adherence AI</h3></div>')

        with gr.Row():
            patient_dd  = gr.Dropdown(label="Select Patient", choices=[], interactive=True)
            refresh_btn = gr.Button("🔄 Refresh", variant="secondary", size="sm")

        with gr.Tabs():
            with gr.TabItem("Add / Stop Medication"):
                with gr.Row():
                    with gr.Column():
                        gr.HTML('<div style="color:#94A3B8;font-size:0.8rem;font-weight:600;margin-bottom:8px;">ADD MEDICATION</div>')
                        med_name_in  = gr.Textbox(label="Medicine Name", placeholder="e.g. Paracetamol 500mg")
                        dosage_in    = gr.Textbox(label="Dosage", placeholder="e.g. 1 tablet")
                        freq_in      = gr.Dropdown(label="Frequency", choices=FREQUENCIES, value="Once daily")
                        duration_in  = gr.Number(label="Duration (days)", value=7, minimum=1)
                        notes_in     = gr.Textbox(label="Notes (optional)", placeholder="Take after food")
                        add_btn      = gr.Button("Add Medication", variant="primary")
                        add_out      = gr.Markdown(value="")

                    with gr.Column():
                        gr.HTML('<div style="color:#94A3B8;font-size:0.8rem;font-weight:600;margin-bottom:8px;">STOP MEDICATION</div>')
                        med_id_in    = gr.Number(label="Medication ID to Stop", value=0, minimum=0)
                        stop_btn     = gr.Button("Stop Medication", variant="secondary")
                        stop_out     = gr.Markdown(value="")
                        gr.HTML('<div style="color:#94A3B8;font-size:0.8rem;font-weight:600;margin:16px 0 8px;">ACTIVE MEDICATIONS</div>')
                        active_out   = gr.Markdown(value="*Select a patient to view active medications.*")

            with gr.TabItem("Log Dose"):
                with gr.Row():
                    with gr.Column():
                        dose_med_id  = gr.Number(label="Medication ID", value=0, minimum=0)
                        dose_taken   = gr.Checkbox(label="Dose Taken?", value=True)
                        dose_notes   = gr.Textbox(label="Notes (optional)", placeholder="e.g. Took late")
                        log_btn      = gr.Button("Log Dose", variant="primary")
                        log_out      = gr.Markdown(value="")
                    with gr.Column():
                        adherence_tbl = gr.Dataframe(label="Adherence Log",
                                                      headers=["Med ID", "Name", "Scheduled", "Taken", "Notes"],
                                                      interactive=False)

            with gr.TabItem("AI Adherence Analysis"):
                analyze_btn  = gr.Button("Analyze Adherence with Gemma", variant="primary")
                analysis_out = gr.Markdown(value="*Select a patient and click Analyze.*")
                model_badge  = gr.Textbox(label="Model", interactive=False, value="—")

        # ── Handlers ──
        def do_refresh():
            return gr.update(choices=get_patient_dropdown_choices())

        def load_meds(pid_label):
            if not pid_label:
                return "*Select a patient.*"
            try:
                pid = int(pid_label.split("|")[0].strip())
                return get_active_meds_display(pid)
            except Exception:
                return "*Error loading medications.*"

        def do_add(pid_label, name, dosage, freq, duration, notes):
            if not pid_label:
                return "⚠️ Select a patient first.", "*Select a patient.*"
            try:
                pid = int(pid_label.split("|")[0].strip())
            except Exception:
                return "⚠️ Invalid patient.", "*Select a patient.*"
            msg = add_med(pid, name, dosage, freq, int(duration), notes)
            return msg, get_active_meds_display(pid)

        def do_stop(pid_label, med_id):
            if not pid_label:
                return "⚠️ Select a patient first.", "*Select a patient.*"
            try:
                pid = int(pid_label.split("|")[0].strip())
            except Exception:
                return "⚠️ Invalid patient.", "*Select a patient.*"
            msg = stop_med(int(med_id))
            return msg, get_active_meds_display(pid)

        def do_log(pid_label, med_id, taken, notes):
            if not pid_label:
                return "⚠️ Select a patient first.", None
            try:
                pid = int(pid_label.split("|")[0].strip())
            except Exception:
                return "⚠️ Invalid patient.", None
            msg = log_dose(int(med_id), taken, notes)
            tbl = get_adherence_table(pid)
            return msg, tbl

        def do_analysis(pid_label):
            if not pid_label:
                return "⚠️ Select a patient first.", "—"
            try:
                pid = int(pid_label.split("|")[0].strip())
            except Exception:
                return "⚠️ Invalid patient.", "—"
            result, model = run_adherence_analysis(pid)
            return result, model

        refresh_btn.click(do_refresh, outputs=[patient_dd])
        patient_dd.change(load_meds, inputs=[patient_dd], outputs=[active_out])
        add_btn.click(do_add,
                      inputs=[patient_dd, med_name_in, dosage_in, freq_in, duration_in, notes_in],
                      outputs=[add_out, active_out])
        stop_btn.click(do_stop, inputs=[patient_dd, med_id_in], outputs=[stop_out, active_out])
        log_btn.click(do_log, inputs=[patient_dd, dose_med_id, dose_taken, dose_notes],
                      outputs=[log_out, adherence_tbl])
        analyze_btn.click(do_analysis, inputs=[patient_dd], outputs=[analysis_out, model_badge])
