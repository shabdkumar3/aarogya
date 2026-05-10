import gradio as gr
from modules.patient import register_patient, format_patient_card, LANGUAGES, GENDERS
from database.queries import get_patient_dropdown_choices


def build_registry_tab():
    with gr.TabItem("📋 Patient Registry"):
        gr.HTML('<div class="section-header"><div class="section-icon">📋</div><h3>Register & View Patients</h3></div>')
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML('<div style="color:#94A3B8;font-size:0.8rem;font-weight:600;margin-bottom:12px;">NEW PATIENT REGISTRATION</div>')
                name_in   = gr.Textbox(label="Full Name", placeholder="e.g. Priya Sharma")
                age_in    = gr.Number(label="Age", value=30, minimum=1, maximum=120)
                gender_in = gr.Dropdown(label="Gender", choices=GENDERS, value="Female")
                village_in = gr.Textbox(label="Village / Block", placeholder="e.g. Rampur, Sitapur")
                lang_in   = gr.Dropdown(label="Preferred Language", choices=LANGUAGES, value="Hindi")
                phone_in  = gr.Textbox(label="Phone Number (optional)", placeholder="+91-XXXXXXXXXX")
                reg_btn   = gr.Button("Register Patient", variant="primary")
                reg_out   = gr.Markdown(value="", label="Registration Status")

            with gr.Column(scale=1):
                gr.HTML('<div style="color:#94A3B8;font-size:0.8rem;font-weight:600;margin-bottom:12px;">VIEW PATIENT RECORD</div>')
                patient_dd = gr.Dropdown(label="Select Patient", choices=[], interactive=True)
                refresh_btn = gr.Button("🔄 Refresh List", variant="secondary")
                patient_card = gr.Markdown(value="*Select a patient to view their record.*")

        def do_register(name, age, gender, village, lang, phone):
            msg, pid = register_patient(name, int(age), gender, village, lang, phone)
            choices = get_patient_dropdown_choices()
            return msg, gr.update(choices=choices)

        def do_refresh():
            return gr.update(choices=get_patient_dropdown_choices())

        def do_view(pid_label):
            if not pid_label:
                return "*No patient selected.*"
            try:
                pid = int(pid_label.split("|")[0].strip())
            except Exception:
                return "*Invalid selection.*"
            return format_patient_card(pid)

        reg_btn.click(do_register,
                      inputs=[name_in, age_in, gender_in, village_in, lang_in, phone_in],
                      outputs=[reg_out, patient_dd])
        refresh_btn.click(do_refresh, outputs=[patient_dd])
        patient_dd.change(do_view, inputs=[patient_dd], outputs=[patient_card])
