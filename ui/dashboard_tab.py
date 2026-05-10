import gradio as gr
from modules.dashboard import get_dashboard_markdown, get_weekly_health_tips


def build_dashboard_tab():
    with gr.TabItem("📊 Dashboard"):
        gr.HTML('<div class="section-header"><div class="section-icon">📊</div><h3>ASHA Field Dashboard</h3></div>')

        with gr.Row():
            with gr.Column(scale=2):
                refresh_btn   = gr.Button("🔄 Refresh Dashboard", variant="primary")
                dashboard_out = gr.Markdown(value="*Click Refresh to load patient statistics.*")

            with gr.Column(scale=1):
                gr.HTML('<div style="color:#94A3B8;font-size:0.78rem;font-weight:700;margin-bottom:8px;letter-spacing:.05em">WEEKLY HEALTH TIPS</div>')
                tips_btn   = gr.Button("Generate Tips with Gemma", variant="secondary")
                tips_out   = gr.Markdown(value="*Click to generate AI-powered health tips for ASHA workers.*")
                tips_model = gr.Textbox(label="Model", interactive=False, value="—")

        def do_refresh():
            return get_dashboard_markdown()

        def do_tips():
            tips, model = get_weekly_health_tips()
            return tips, model

        refresh_btn.click(do_refresh, outputs=[dashboard_out])
        tips_btn.click(do_tips, outputs=[tips_out, tips_model])
