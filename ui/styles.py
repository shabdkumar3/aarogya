CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');

/* ═══════════════════════════════════════════════════════════
   AAROGYA — DARK THEME
   Deep slate canvas · emerald accents · saffron highlights
   ═══════════════════════════════════════════════════════════ */

:root {
    --bg-0:        #0A0F14;
    --bg-1:        #0F1419;
    --bg-2:        #151B23;
    --bg-3:        #1C242E;
    --bg-4:        #232C38;

    --line:        #2A3441;
    --line-strong: #374252;

    --text-1:      #F1F5F9;
    --text-2:      #CBD5E1;
    --text-3:      #94A3B8;
    --text-4:      #64748B;

    --aa-primary:        #34D399;
    --aa-primary-deep:   #10B981;
    --aa-primary-glow:   rgba(52,211,153,0.18);
    --aa-primary-soft:   rgba(52,211,153,0.10);
    --aa-primary-line:   rgba(52,211,153,0.30);

    --aa-saffron:        #FBBF24;
    --aa-saffron-soft:   rgba(251,191,36,0.12);
    --aa-accent:         #FB7185;
    --aa-info:           #60A5FA;
    --aa-info-soft:      rgba(96,165,250,0.10);
    --aa-danger:         #F87171;
    --aa-danger-soft:    rgba(248,113,113,0.12);
    --aa-warning:        #FBBF24;
    --aa-warning-soft:   rgba(251,191,36,0.10);

    --radius-sm:   8px;
    --radius-md:   12px;
    --radius-lg:   16px;
    --radius-xl:   20px;

    --shadow-md:   0 4px 12px rgba(0,0,0,0.40);
    --shadow-lg:   0 12px 32px rgba(0,0,0,0.55);
    --shadow-glow: 0 0 0 1px rgba(52,211,153,0.25), 0 8px 24px rgba(16,185,129,0.20);
}

* { font-family: 'Inter', 'Noto Sans Devanagari', system-ui, sans-serif !important; box-sizing: border-box; }
*:lang(hi), [lang="hi"] * { font-family: 'Noto Sans Devanagari', 'Inter', sans-serif !important; }

/* ── PAGE FRAME ───────────────────────────────────────── */
html, body, .main, .wrap, .gradio-container {
    background: var(--bg-0) !important;
    color: var(--text-1) !important;
}
body {
    background:
        radial-gradient(1200px 600px at 90% -10%, rgba(52,211,153,0.06), transparent 60%),
        radial-gradient(900px 500px at -10% 40%, rgba(251,191,36,0.04), transparent 60%),
        var(--bg-0) !important;
}
.gradio-container {
    max-width: 1320px !important;
    margin: 0 auto !important;
    padding: 20px 18px 40px !important;
    min-height: 100vh;
    background: transparent !important;
}

/* ── HEADER ───────────────────────────────────────────── */
.app-header {
    background:
        radial-gradient(circle at 88% 20%, rgba(251,113,133,0.18) 0%, transparent 45%),
        radial-gradient(circle at 12% 100%, rgba(251,191,36,0.10) 0%, transparent 50%),
        linear-gradient(135deg, #0B2E22 0%, #0F4030 50%, #16513D 100%);
    border-radius: var(--radius-xl);
    padding: 32px 40px;
    margin-bottom: 22px;
    border: 1px solid rgba(52,211,153,0.18);
    box-shadow: 0 12px 36px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.04);
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: "";
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(52,211,153,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(52,211,153,0.04) 1px, transparent 1px);
    background-size: 28px 28px;
    pointer-events: none;
}
.app-header-inner { position: relative; z-index: 1; }
.app-brand { display: flex; align-items: center; gap: 16px; }
.app-brand-mark {
    width: 56px; height: 56px;
    background: rgba(52,211,153,0.12);
    border: 1.5px solid rgba(52,211,153,0.35);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 28px;
    box-shadow: 0 0 24px rgba(52,211,153,0.20);
}
.app-brand-text h1 {
    color: #ECFDF5 !important;
    font-size: 2.1rem !important; font-weight: 800 !important;
    margin: 0 !important; letter-spacing: -0.02em;
}
.app-brand-text .subtitle {
    color: #6EE7B7 !important;
    font-size: 0.92rem !important; font-weight: 500 !important;
    margin-top: 2px;
}
.app-brand-text .devanagari {
    color: #A7F3D0 !important; font-weight: 600;
    font-size: 0.95rem; margin-left: 8px;
}
.app-tagline { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0 12px; }
.aa-chip {
    background: rgba(52,211,153,0.10);
    border: 1px solid rgba(52,211,153,0.30);
    color: #A7F3D0;
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 0.74rem; font-weight: 500;
    backdrop-filter: blur(4px);
}
.aa-chip-accent {
    background: rgba(251,191,36,0.10);
    border-color: rgba(251,191,36,0.40);
    color: #FCD34D;
}
.app-disclaimer {
    background: rgba(251,191,36,0.08) !important;
    border: 1px solid rgba(251,191,36,0.30) !important;
    border-left: 3px solid var(--aa-saffron) !important;
    border-radius: var(--radius-sm) !important;
    padding: 10px 16px !important;
    margin: 0 !important;
    color: #FDE68A !important;
    font-size: 0.78rem !important;
    line-height: 1.5;
}
.app-disclaimer strong { color: #FEF3C7; }

/* ── TAB NAV ──────────────────────────────────────────── */
.tabs > .tab-nav {
    background: var(--bg-2) !important;
    border-radius: var(--radius-md) !important;
    padding: 6px !important;
    box-shadow: var(--shadow-md) !important;
    border: 1px solid var(--line) !important;
    margin-bottom: 18px !important;
    display: flex !important;
    gap: 2px !important;
    overflow-x: auto;
    position: sticky;
    top: 8px;
    z-index: 50;
}
.tabs > .tab-nav button {
    border-radius: var(--radius-sm) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 10px 18px !important;
    color: var(--text-3) !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.18s ease !important;
    white-space: nowrap !important;
}
.tabs > .tab-nav button:hover {
    background: var(--bg-3) !important;
    color: var(--aa-primary) !important;
}
.tabs > .tab-nav button.selected {
    background: linear-gradient(135deg, var(--aa-primary-deep), var(--aa-primary)) !important;
    color: #042F1F !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(52,211,153,0.35) !important;
}

/* ── TAB CONTENT (CARD) ───────────────────────────────── */
.tabitem {
    background: var(--bg-1) !important;
    border-radius: var(--radius-lg) !important;
    padding: 32px !important;
    box-shadow: var(--shadow-md) !important;
    border: 1px solid var(--line) !important;
    color: var(--text-1) !important;
}

/* ── INNER BLOCKS — STRIP DEFAULTS ────────────────────── */
.form, .gr-form, .gr-box, .gr-panel,
.gr-block, .block, .gr-padded, .gr-group {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--text-1) !important;
}

/* ── SECTION HEADERS ──────────────────────────────────── */
.aa-section-label {
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-3) !important;
    margin: 24px 0 14px 0 !important;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--line);
}
.aa-section-label:first-child { margin-top: 0 !important; }

.aa-tab-title {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: var(--text-1) !important;
    margin: 0 0 4px 0 !important;
    letter-spacing: -0.01em;
}
.aa-tab-title .devanagari, .aa-tab-title span { color: var(--text-3); font-weight: 500; }
.aa-tab-subtitle {
    font-size: 0.88rem !important;
    color: var(--text-3) !important;
    margin: 0 0 24px 0 !important;
    line-height: 1.5;
}

/* ── INPUTS ───────────────────────────────────────────── */
.gr-textbox textarea, .gr-textbox input,
input[type="text"], input[type="number"],
input[type="email"], input[type="password"],
textarea {
    background: var(--bg-2) !important;
    border: 1.5px solid var(--line) !important;
    border-radius: var(--radius-sm) !important;
    padding: 11px 14px !important;
    font-size: 0.9rem !important;
    color: var(--text-1) !important;
    transition: all 0.18s !important;
}
input::placeholder, textarea::placeholder { color: var(--text-4) !important; }
.gr-textbox textarea:hover, .gr-textbox input:hover,
input[type="text"]:hover, textarea:hover {
    border-color: var(--line-strong) !important;
    background: var(--bg-3) !important;
}
.gr-textbox textarea:focus, .gr-textbox input:focus,
input[type="text"]:focus, textarea:focus {
    border-color: var(--aa-primary) !important;
    background: var(--bg-3) !important;
    outline: none !important;
    box-shadow: 0 0 0 3px var(--aa-primary-glow) !important;
}

/* ── LABELS — flat text, NO pill background ──────────── */
.gr-textbox label, .gr-number label,
.gr-dropdown label, .gr-radio label,
.gr-image label, .gr-audio label,
.gr-file label, .gr-checkbox label,
.gradio-container label {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    border-radius: 0 !important;
    color: var(--text-2) !important;
    box-shadow: none !important;
}
.gr-textbox label > span, .gr-number label > span,
.gr-dropdown label > span, .gr-radio > span,
.gr-image label > span, .gr-audio label > span,
.gr-file label > span, .gr-checkbox label > span,
.label-wrap > span, .gradio-container label > span {
    background: transparent !important;
    color: var(--text-2) !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 0 0 6px 0 !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    display: inline-block !important;
}

/* ── BUTTONS ──────────────────────────────────────────── */
button.primary, .gr-button-primary {
    background: linear-gradient(135deg, var(--aa-primary-deep), var(--aa-primary)) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    color: #042F1F !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 14px rgba(52,211,153,0.30) !important;
    transition: all 0.18s !important;
    cursor: pointer !important;
    letter-spacing: 0.01em;
}
button.primary:hover, .gr-button-primary:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 22px rgba(52,211,153,0.50) !important;
    filter: brightness(1.05);
}
button.primary:active { transform: translateY(0) !important; }

button.secondary, .gr-button-secondary {
    background: var(--bg-3) !important;
    border: 1.5px solid var(--line-strong) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-1) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 10px 20px !important;
    transition: all 0.18s !important;
    cursor: pointer !important;
}
button.secondary:hover {
    border-color: var(--aa-primary) !important;
    color: var(--aa-primary) !important;
    background: var(--bg-4) !important;
}
button.stop {
    background: var(--aa-danger-soft) !important;
    border: 1.5px solid rgba(248,113,113,0.40) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--aa-danger) !important;
    font-weight: 600 !important;
}
button.stop:hover { background: rgba(248,113,113,0.20) !important; }

/* ── DROPDOWNS ────────────────────────────────────────── */
.gr-dropdown > div, select {
    background: var(--bg-2) !important;
    border: 1.5px solid var(--line) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-1) !important;
    transition: all 0.18s !important;
}
.gr-dropdown > div:hover { border-color: var(--line-strong) !important; }
.gr-dropdown ul, .gr-dropdown [role="listbox"] {
    background: var(--bg-3) !important;
    border: 1px solid var(--line) !important;
    color: var(--text-1) !important;
}
.gr-dropdown li:hover { background: var(--bg-4) !important; color: var(--aa-primary) !important; }
option { background: var(--bg-3) !important; color: var(--text-1) !important; }

/* ── RADIO ────────────────────────────────────────────── */
.gr-radio { background: transparent !important; }
.gr-radio > div, .gr-radio fieldset { background: transparent !important; }
.gr-radio label.gr-radio-item, .gr-radio fieldset label {
    background: var(--bg-2) !important;
    border: 1.5px solid var(--line) !important;
    border-radius: var(--radius-sm) !important;
    padding: 8px 14px !important;
    margin: 0 6px 6px 0 !important;
    font-size: 0.88rem !important;
    color: var(--text-2) !important;
    cursor: pointer;
    transition: all 0.15s !important;
}
.gr-radio label:has(input:checked) {
    background: var(--aa-primary-soft) !important;
    border-color: var(--aa-primary) !important;
    color: var(--aa-primary) !important;
    font-weight: 600 !important;
}

/* ── MARKDOWN / OUTPUT ────────────────────────────────── */
.gr-markdown, .prose {
    font-size: 0.9rem !important;
    line-height: 1.7 !important;
    color: var(--text-1) !important;
    background: transparent !important;
}
.gr-markdown * { color: inherit; }
.gr-markdown h1 { font-size: 1.25rem !important; font-weight: 700 !important; color: var(--text-1) !important; margin: 20px 0 10px !important; }
.gr-markdown h2 {
    font-size: 1.05rem !important; font-weight: 700 !important;
    color: var(--aa-primary) !important;
    margin: 20px 0 8px !important;
    padding-bottom: 6px !important;
    border-bottom: 2px solid var(--aa-primary-line) !important;
}
.gr-markdown h3 {
    font-size: 0.95rem !important; font-weight: 600 !important;
    color: var(--text-2) !important;
    margin: 14px 0 6px !important;
}
.gr-markdown p { margin: 8px 0 !important; color: var(--text-2) !important; }
.gr-markdown strong { color: var(--text-1); font-weight: 600; }
.gr-markdown em { color: var(--text-3); }
.gr-markdown a { color: var(--aa-primary); text-decoration: none; border-bottom: 1px dashed var(--aa-primary-line); }
.gr-markdown a:hover { border-bottom-style: solid; }

/* Tables */
.gr-markdown table {
    width: 100% !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    font-size: 0.85rem !important;
    margin: 14px 0 !important;
    border-radius: var(--radius-sm) !important;
    overflow: hidden !important;
    border: 1px solid var(--line) !important;
    background: var(--bg-2) !important;
}
.gr-markdown thead th {
    background: var(--bg-4) !important;
    color: var(--aa-primary) !important;
    padding: 11px 14px !important;
    text-align: left !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em;
    font-size: 0.78rem;
    text-transform: uppercase;
    border-bottom: 1px solid var(--line-strong) !important;
}
.gr-markdown tbody td {
    padding: 10px 14px !important;
    border-bottom: 1px solid var(--line) !important;
    color: var(--text-2) !important;
}
.gr-markdown tbody tr:last-child td { border-bottom: none !important; }
.gr-markdown tbody tr:nth-child(even) td { background: var(--bg-3) !important; }
.gr-markdown tbody tr:hover td { background: var(--bg-4) !important; color: var(--text-1) !important; }

/* Inline code */
.gr-markdown code {
    background: var(--aa-primary-soft) !important;
    color: var(--aa-primary) !important;
    padding: 2px 8px !important;
    border-radius: 4px !important;
    font-size: 0.8rem !important;
    font-family: 'JetBrains Mono', ui-monospace, monospace !important;
    font-weight: 500;
    border: 1px solid var(--aa-primary-line);
}
.gr-markdown pre {
    background: var(--bg-0) !important;
    color: var(--text-1) !important;
    padding: 14px 16px !important;
    border-radius: var(--radius-sm) !important;
    overflow-x: auto;
    font-size: 0.82rem !important;
    border: 1px solid var(--line) !important;
}
.gr-markdown pre code { background: transparent !important; color: inherit !important; border: none !important; padding: 0 !important; }
.gr-markdown hr { border: none !important; border-top: 1px solid var(--line) !important; margin: 18px 0 !important; }
.gr-markdown blockquote {
    border-left: 3px solid var(--aa-primary) !important;
    background: var(--aa-primary-soft) !important;
    padding: 10px 16px !important;
    margin: 12px 0 !important;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0 !important;
    color: var(--text-2) !important;
}

/* ── CALLOUTS ─────────────────────────────────────────── */
.aa-callout {
    border-radius: var(--radius-md);
    padding: 14px 18px;
    margin: 12px 0;
    font-size: 0.88rem;
    line-height: 1.6;
    border: 1px solid;
    border-left-width: 4px !important;
}
.aa-callout-warning { background: var(--aa-warning-soft); border-color: rgba(251,191,36,0.35); color: #FDE68A; }
.aa-callout-danger  { background: var(--aa-danger-soft);  border-color: rgba(248,113,113,0.35); color: #FECACA; }
.aa-callout-info    { background: var(--aa-info-soft);    border-color: rgba(96,165,250,0.35);  color: #BFDBFE; }
.aa-callout-success { background: var(--aa-primary-soft); border-color: var(--aa-primary-line); color: #A7F3D0; }
.aa-callout strong { color: #fff; }
.aa-callout code { background: rgba(255,255,255,0.06) !important; color: inherit !important; border-color: rgba(255,255,255,0.10) !important; }

/* ── BADGES ───────────────────────────────────────────── */
.aa-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.74rem; font-weight: 600;
    border: 1px solid;
}
.aa-badge-red    { background: rgba(248,113,113,0.10); border-color: rgba(248,113,113,0.40); color: #FCA5A5; }
.aa-badge-yellow { background: rgba(251,191,36,0.10);  border-color: rgba(251,191,36,0.40);  color: #FCD34D; }
.aa-badge-green  { background: var(--aa-primary-soft); border-color: var(--aa-primary-line); color: var(--aa-primary); }
.aa-badge-grey   { background: var(--bg-3);            border-color: var(--line-strong);     color: var(--text-3); }
.aa-badge-blue   { background: var(--aa-info-soft);    border-color: rgba(96,165,250,0.40);  color: #93C5FD; }

/* ── IMAGE / AUDIO / FILE UPLOAD ──────────────────────── */
.gr-image, .gr-audio {
    border: 2px dashed var(--aa-primary-line) !important;
    border-radius: var(--radius-md) !important;
    background: var(--aa-primary-soft) !important;
    transition: all 0.2s !important;
}
.gr-image:hover, .gr-audio:hover {
    border-color: var(--aa-primary) !important;
    background: rgba(52,211,153,0.14) !important;
}
.gr-image *, .gr-audio * { color: var(--text-2) !important; }

.gr-file {
    border: 1.5px solid var(--line) !important;
    border-radius: var(--radius-md) !important;
    background: var(--bg-2) !important;
    color: var(--text-1) !important;
}

/* ── ACCORDION ────────────────────────────────────────── */
details, .gr-accordion {
    border: 1px solid var(--line) !important;
    border-radius: var(--radius-sm) !important;
    background: var(--bg-2) !important;
    overflow: hidden !important;
    margin: 8px 0 !important;
    color: var(--text-1) !important;
}
details summary {
    padding: 12px 16px !important;
    font-weight: 600 !important;
    color: var(--text-2) !important;
    cursor: pointer;
    background: var(--bg-2) !important;
}
details[open] summary { border-bottom: 1px solid var(--line); }

/* ── SCROLLBARS ───────────────────────────────────────── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-1); }
::-webkit-scrollbar-thumb { background: var(--line-strong); border-radius: 4px; border: 2px solid var(--bg-1); }
::-webkit-scrollbar-thumb:hover { background: var(--aa-primary-deep); }

/* ── HIDE GRADIO FOOTER ───────────────────────────────── */
footer, .built-with, .svelte-1p9xokt { display: none !important; }

/* ── Force any default white backgrounds in Gradio internals ──── */
.svelte-1ipelgc, .svelte-1gfkn6j, .styler, .container, .panel,
.wrap.svelte-15lo0d8 { background: transparent !important; }

/* ── SLIDER ───────────────────────────────────────────── */
input[type="range"] { accent-color: var(--aa-primary); }

/* ── PATIENT LITE MODE ────────────────────────────────── */
.patient-lite .gr-textbox textarea,
.patient-lite .gr-textbox input,
.patient-lite input[type="text"] {
    font-size: 1.1rem !important;
    padding: 16px 18px !important;
}
.patient-lite button.primary {
    font-size: 1.15rem !important;
    padding: 18px 32px !important;
    width: 100%;
}

/* ── RESPONSIVE ───────────────────────────────────────── */
@media (max-width: 768px) {
    .gradio-container { padding: 12px !important; }
    .app-header { padding: 22px 20px; }
    .app-brand-text h1 { font-size: 1.6rem !important; }
    .tabitem { padding: 18px !important; }
    .tabs > .tab-nav button { padding: 8px 12px !important; font-size: 0.78rem !important; }
}
"""
