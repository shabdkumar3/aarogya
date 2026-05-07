import gradio as gr
from modules.dashboard import get_dashboard_markdown, get_weekly_health_tips


def build_dashboard_tab():
    with gr.Tab("📊  Dashboard"):
        gr.HTML("""
        <div class="aa-tab-title">ASHA Worker Dashboard</div>
        <div class="aa-tab-subtitle">All patients grouped by risk — see who needs attention first.</div>
        """)

        # Action buttons — own row
        with gr.Row():
            refresh_btn = gr.Button("🔄  Refresh Dashboard", variant="primary", scale=1)

        # Legend
        gr.HTML("""
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 20px 0">
          <span class="aa-badge aa-badge-red">🔴 At Risk</span>
          <span class="aa-badge aa-badge-yellow">🟡 Needs Attention</span>
          <span class="aa-badge aa-badge-green">🟢 Stable</span>
          <span class="aa-badge aa-badge-grey">🆕 New</span>
        </div>
        """)

        dashboard_out = gr.Markdown("*Click Refresh Dashboard to load patient list.*")

        gr.HTML('<div class="aa-section-label" style="margin-top:32px">Weekly Health Tips</div>')

        # Tips inputs — clean row
        with gr.Row():
            focus_in  = gr.Textbox(label="Focus Area", value="seasonal diseases", scale=3, placeholder="e.g. monsoon diseases, child nutrition")
            tips_lang = gr.Dropdown(label="Language", choices=["Hindi", "English"], value="Hindi", scale=1)
            tips_btn  = gr.Button("💡  Generate Tips", variant="primary", scale=1)

        tips_out = gr.Markdown("")

        refresh_btn.click(fn=get_dashboard_markdown, outputs=dashboard_out)
        tips_btn.click(fn=get_weekly_health_tips, inputs=[focus_in, tips_lang], outputs=tips_out)
