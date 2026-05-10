import gradio as gr
import os
import socket
from database.schema import initialize_database
from ui.registry_tab import build_registry_tab
from ui.diagnoscan_tab import build_diagnoscan_tab
from ui.medtrack_tab import build_medtrack_tab
from ui.dashboard_tab import build_dashboard_tab
from ui.patient_lite_tab import build_patient_lite_tab
from ui.reports_tab import build_reports_tab
from ui.styles import CUSTOM_CSS
from dotenv import load_dotenv

load_dotenv()


def _find_open_port(start=7860, end=7900):
    for p in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return 0  # let OS pick


def main():
    initialize_database()

    dark_theme = gr.themes.Base(
        primary_hue="emerald",
        secondary_hue="emerald",
        neutral_hue="slate",
    ).set(
        body_background_fill="#0A0F14",
        body_background_fill_dark="#0A0F14",
        background_fill_primary="#0F1419",
        background_fill_primary_dark="#0F1419",
        background_fill_secondary="#151B23",
        background_fill_secondary_dark="#151B23",
        body_text_color="#F1F5F9",
        body_text_color_dark="#F1F5F9",
        block_background_fill="#0F1419",
        block_background_fill_dark="#0F1419",
        block_border_color="#2A3441",
        block_border_color_dark="#2A3441",
        block_label_background_fill="transparent",
        block_label_background_fill_dark="transparent",
        block_label_text_color="#CBD5E1",
        block_label_text_color_dark="#CBD5E1",
        input_background_fill="#151B23",
        input_background_fill_dark="#151B23",
        input_border_color="#2A3441",
        input_border_color_dark="#2A3441",
        border_color_primary="#2A3441",
        border_color_primary_dark="#2A3441",
    )

    # theme and css go in gr.Blocks() — not in launch()
    with gr.Blocks(
        title="Aarogya — AI Health Companion",
        theme=dark_theme,
        css=CUSTOM_CSS,
    ) as app:

        gr.HTML("""
        <div class="app-header">
          <div class="app-header-inner">
            <div class="app-brand">
              <div class="app-brand-mark">🌿</div>
              <div class="app-brand-text">
                <h1>Aarogya <span class="devanagari">आरोग्य</span></h1>
                <div class="subtitle">AI Health Companion for ASHA Workers &amp; Rural Patients</div>
              </div>
            </div>
            <div class="app-tagline">
              <span class="aa-chip">🧠 Gemma 4 Multimodal</span>
              <span class="aa-chip">🌐 Hindi · English · Tamil</span>
              <span class="aa-chip">⚙️ Native Function Calling</span>
              <span class="aa-chip aa-chip-accent">📡 Offline via Ollama</span>
              <span class="aa-chip aa-chip-accent">🔥 Fine-tuned with Unsloth</span>
            </div>
            <div class="app-disclaimer">
              ⚠️ <strong>Medical Disclaimer:</strong> Aarogya provides triage support only.
              It does <strong>not</strong> replace clinical diagnosis by a qualified doctor.
            </div>
          </div>
        </div>
        """)

        with gr.Tabs():
            build_registry_tab()
            build_diagnoscan_tab()
            build_medtrack_tab()
            build_dashboard_tab()
            build_patient_lite_tab()
            build_reports_tab()

        gr.HTML("""
        <div class="app-footer">
          Built with ❤️ for rural India &nbsp;|&nbsp;
          <a href="https://github.com/shabdkumar3/aarogya" target="_blank">GitHub</a> &nbsp;|&nbsp;
          Powered by <strong>Gemma 4</strong> via Google AI Studio &nbsp;|&nbsp;
          Kaggle &times; Google DeepMind Hackathon 2026
        </div>
        """)

    # Detect environment
    is_hosted = bool(os.getenv("SPACE_ID") or os.getenv("GRADIO_SERVER_NAME"))
    if is_hosted:
        host = "0.0.0.0"
        port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
        share = False
        inbrowser = False
    else:
        host = "127.0.0.1"
        port = _find_open_port()
        share = False
        inbrowser = True

    print(f"\n[Aarogya] Starting on http://{host}:{port}  (hosted={is_hosted})\n")
    app.launch(
        server_name=host,
        server_port=port,
        share=share,
        inbrowser=inbrowser,
    )


if __name__ == "__main__":
    main()
