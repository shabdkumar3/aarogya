import gradio as gr
from modules.medtrack import (
    add_med, stop_med, get_active_meds_display,
    log_dose, get_adherence_table, run_adherence_analysis, FREQUENCIES,
)
from database.queries import get_patient_dropdown_choices, parse_dropdown


def build_medtrack_tab():
    with gr.TabItem("💊 MedTrack"):
        gr.HTML('<div class="section-header"><div class="section-icon">💊</div><h3>Medication Tracking &amp; Adherence AI</h3></div>')

        with gr.Row():
            patient_dd  = gr.Dropdown(label="Select Patient", choices=[], interactive=True)
            refresh_btn = gr.Button("🔄 Refresh", variant="secondary", size="sm")

        active_out = gr.Markdown(value="*Select a patient to view active medications.*")

        with gr.Tabs():
            # ── Add / Stop ──────────────────────────────────────────
            with gr.TabItem("➕ Add / Stop Medication"):
                with gr.Row():
                    with gr.Column():
                        gr.HTML('<div style="color:#94A3B8;font-size:0.78rem;font-weight:700;margin-bottom:8px;">ADD MEDICATION</div>')
                        med_name_in  = gr.Textbox(label="Medicine Name *", placeholder="e.g. Paracetamol 500mg")
                        dosage_in    = gr.Textbox(label="Dosage *", placeholder="e.g. 1 tablet")
                        freq_in      = gr.Dropdown(label="Frequency", choices=FREQUENCIES, value="Once daily")
                        duration_in  = gr.Number(label="Duration (days) *", value=7, minimum=1, maximum=365)
                        notes_in     = gr.Textbox(label="Notes (optional)", placeholder="Take after food")
                        add_btn      = gr.Button("Add Medication", variant="primary")
                        add_out      = gr.Markdown(value="")

                    with gr.Column():
                        gr.HTML('<div style="color:#94A3B8;font-size:0.78rem;font-weight:700;margin-bottom:8px;">STOP MEDICATION</div>')
                        med_id_in = gr.Number(label="Medication ID to Stop", value=1, minimum=1)
                        stop_btn  = gr.Button("Stop Medication", variant="secondary")
                        stop_out  = gr.Markdown(value="")

            # ── Log Dose ────────────────────────────────────────────
            with gr.TabItem("📝 Log Dose"):
                with gr.Row():
                    with gr.Column():
                        dose_med_id = gr.Number(label="Medication ID *", value=1, minimum=1)
                        dose_taken  = gr.Checkbox(label="Dose Taken?", value=True)
                        dose_notes  = gr.Textbox(label="Notes (optional)", placeholder="e.g. Took with food")
                        log_btn     = gr.Button("Log Dose", variant="primary")
                        log_out     = gr.Markdown(value="")
                    with gr.Column():
                        adherence_tbl = gr.Dataframe(
                            label="Adherence Log (Last 14 days)",
                            headers=["Date", "Medication", "Dose", "Status"],
                            interactive=False,
                        )

            # ── AI Analysis ─────────────────────────────────────────
            with gr.TabItem("🧠 AI Adherence Analysis"):
                analyze_btn  = gr.Button("Analyze with Gemma", variant="primary")
                analysis_out = gr.Markdown(value="*Select a patient and click Analyze.*")
                model_badge  = gr.Textbox(label="Model Used", interactive=False, value="—")

        # ── Handlers ────────────────────────────────────────────────
        def do_refresh():
            return gr.update(choices=get_patient_dropdown_choices(), value=None)

        def load_meds(selection):
            pid = parse_dropdown(selection)
            if not pid:
                return "*Select a patient.*"
            return get_active_meds_display(pid)

        def do_add(selection, name, dosage, freq, duration, notes):
            pid = parse_dropdown(selection)
            if not pid:
                return "⚠️ Select a patient first.", "*Select a patient.*"
            msg = add_med(pid, name, dosage, freq, duration, notes)
            return msg, get_active_meds_display(pid)

        def do_stop(selection, med_id):
            pid = parse_dropdown(selection)
            msg = stop_med(med_id)
            return msg, get_active_meds_display(pid) if pid else "*Select a patient.*"

        def do_log(selection, med_id, taken, notes):
            pid = parse_dropdown(selection)
            msg = log_dose(med_id, taken, notes)
            tbl = get_adherence_table(pid) if pid else []
            return msg, tbl

        def load_adherence(selection):
            pid = parse_dropdown(selection)
            return get_adherence_table(pid) if pid else []

        def do_analysis(selection):
            pid = parse_dropdown(selection)
            if not pid:
                return "⚠️ Select a patient first.", "—"
            result, model = run_adherence_analysis(pid)
            return result, model

        refresh_btn.click(do_refresh, outputs=[patient_dd])
        patient_dd.change(load_meds,      inputs=[patient_dd], outputs=[active_out])
        patient_dd.change(load_adherence, inputs=[patient_dd], outputs=[adherence_tbl])
        add_btn.click(do_add,
                      inputs=[patient_dd, med_name_in, dosage_in, freq_in, duration_in, notes_in],
                      outputs=[add_out, active_out])
        stop_btn.click(do_stop, inputs=[patient_dd, med_id_in], outputs=[stop_out, active_out])
        log_btn.click(do_log,
                      inputs=[patient_dd, dose_med_id, dose_taken, dose_notes],
                      outputs=[log_out, adherence_tbl])
        analyze_btn.click(do_analysis, inputs=[patient_dd], outputs=[analysis_out, model_badge])
