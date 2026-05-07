import gradio as gr
from modules.patient import register_patient, format_patient_card, LANGUAGES, GENDERS
from database.queries import get_patient_dropdown_choices


def build_registry_tab():
    with gr.Tab("👤  Patient Registry"):
        gr.HTML("""
        <div class="aa-tab-title">Register New Patient</div>
        <div class="aa-tab-subtitle">Add a new patient to the ASHA worker's case list. Fields marked with * are required.</div>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML('<div class="aa-section-label">Personal Details</div>')
                name_in      = gr.Textbox(label="Full Name *", placeholder="e.g. Ramesh Kumar")
                age_in       = gr.Number(label="Age *", value=30, minimum=0, maximum=120, precision=0)
                gender_in    = gr.Radio(label="Gender *", choices=GENDERS, value="Male")
                language_in  = gr.Dropdown(label="Preferred Language", choices=LANGUAGES, value="Hindi")

            with gr.Column(scale=1):
                gr.HTML('<div class="aa-section-label">Location &amp; Medical History</div>')
                village_in    = gr.Textbox(label="Village *", placeholder="e.g. Mandawa")
                district_in   = gr.Textbox(label="District", placeholder="e.g. Jhunjhunu")
                conditions_in = gr.Textbox(label="Existing Conditions", placeholder="e.g. Diabetes, Hypertension", lines=2)
                allergies_in  = gr.Textbox(label="Known Allergies", placeholder="e.g. Penicillin", lines=2)

        register_btn = gr.Button("➕  Register Patient", variant="primary", size="lg")
        status_out   = gr.Markdown("")

        gr.HTML('<div class="aa-section-label" style="margin-top:32px">Patient Records</div>')

        with gr.Row():
            patient_dd  = gr.Dropdown(label="Select Patient", choices=get_patient_dropdown_choices(), interactive=True, scale=5)
            refresh_btn = gr.Button("🔄  Refresh", scale=1, variant="secondary")

        patient_card = gr.Markdown("*Select a patient from the dropdown to view their details.*")

        def on_register(name, age, gender, village, district, language, cond, allg):
            _, msg, _ = register_patient(name, age, gender, village, district, language, cond, allg)
            return msg, gr.update(choices=get_patient_dropdown_choices())

        register_btn.click(fn=on_register,
                           inputs=[name_in, age_in, gender_in, village_in, district_in, language_in, conditions_in, allergies_in],
                           outputs=[status_out, patient_dd])
        refresh_btn.click(fn=lambda: gr.update(choices=get_patient_dropdown_choices()), outputs=patient_dd)
        patient_dd.change(fn=format_patient_card, inputs=patient_dd, outputs=patient_card)

    return patient_dd
