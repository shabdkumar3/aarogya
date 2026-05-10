"""Aarogya — Dark UI Theme CSS"""

CUSTOM_CSS = """
/* ═══════════════════════════════════════════════════════════
   ROOT VARIABLES — Indian Health Design System
   ═══════════════════════════════════════════════════════════ */
:root {
  --bg-0: #0A0F14;
  --bg-1: #0F1419;
  --bg-2: #151B23;
  --bg-3: #1A2332;
  --border: #2A3441;
  --border-bright: #3D4F63;
  --aa-primary: #34D399;
  --aa-primary-deep: #10B981;
  --aa-primary-dim: #065F46;
  --aa-saffron: #FBBF24;
  --aa-saffron-dim: #78350F;
  --aa-danger: #F87171;
  --aa-danger-dim: #7F1D1D;
  --aa-blue: #60A5FA;
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --shadow-card: 0 4px 24px rgba(0,0,0,0.5);
}

/* ═══ BASE ═══ */
body, .gradio-container, .main, #root {
  background: var(--bg-0) !important;
  color: var(--text-primary) !important;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
}

.gradio-container {
  max-width: 1400px !important;
  margin: 0 auto !important;
  padding: 0 !important;
}

/* ═══ HEADER ═══ */
.app-header {
  background: linear-gradient(135deg, #0A2E1A 0%, #0F1419 40%, #0A1628 100%);
  border-bottom: 1px solid var(--border-bright);
  padding: 20px 32px;
  position: relative;
  overflow: hidden;
}
.app-header::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(52,211,153,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(52,211,153,0.04) 1px, transparent 1px);
  background-size: 32px 32px;
  pointer-events: none;
}
.app-header-inner { position: relative; z-index: 1; }
.app-brand { display: flex; align-items: center; gap: 16px; margin-bottom: 12px; }
.app-brand-mark {
  width: 52px; height: 52px;
  background: linear-gradient(135deg, var(--aa-primary), var(--aa-primary-deep));
  border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  font-size: 26px;
  box-shadow: 0 0 24px rgba(52,211,153,0.3);
}
.app-brand-text h1 {
  margin: 0 !important; padding: 0 !important;
  font-size: 2rem !important; font-weight: 800 !important;
  color: var(--text-primary) !important;
  letter-spacing: -0.5px;
}
.app-brand-text h1 .devanagari {
  color: var(--aa-primary) !important;
  font-size: 1.4rem !important;
  margin-left: 8px;
}
.subtitle {
  color: var(--text-secondary) !important;
  font-size: 0.85rem;
  margin-top: 2px;
}
.app-tagline { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.aa-chip {
  background: rgba(52,211,153,0.1);
  border: 1px solid rgba(52,211,153,0.25);
  color: var(--aa-primary);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
}
.aa-chip-accent {
  background: rgba(251,191,36,0.1);
  border-color: rgba(251,191,36,0.25);
  color: var(--aa-saffron);
}
.app-disclaimer {
  font-size: 0.75rem;
  color: var(--text-muted);
  padding: 6px 12px;
  background: rgba(248,113,113,0.06);
  border: 1px solid rgba(248,113,113,0.15);
  border-radius: var(--radius-sm);
  display: inline-block;
}

/* ═══ TABS ═══ */
.tabs { background: var(--bg-0) !important; }
.tab-nav {
  background: var(--bg-1) !important;
  border-bottom: 1px solid var(--border) !important;
  padding: 0 24px !important;
  position: sticky !important;
  top: 0 !important;
  z-index: 100 !important;
}
.tab-nav button {
  background: transparent !important;
  color: var(--text-secondary) !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  padding: 14px 20px !important;
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
  border-radius: 0 !important;
  margin: 0 2px !important;
}
.tab-nav button:hover {
  color: var(--text-primary) !important;
  background: rgba(255,255,255,0.03) !important;
}
.tab-nav button.selected {
  color: var(--aa-primary) !important;
  border-bottom-color: var(--aa-primary) !important;
  background: transparent !important;
}

/* ═══ BLOCKS & PANELS ═══ */
.gr-block, .gr-box, .gr-panel,
div[class*="block"], div[class*="panel"],
div[class*="container"], .tabitem {
  background: var(--bg-1) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  color: var(--text-primary) !important;
}

/* ═══ INPUTS ═══ */
input[type="text"], input[type="number"], input[type="email"],
textarea, select,
.gr-textbox textarea, .gr-textbox input,
div[class*="input"] input, div[class*="input"] textarea {
  background: var(--bg-2) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  padding: 10px 14px !important;
}
input:focus, textarea:focus, select:focus {
  border-color: var(--aa-primary) !important;
  outline: none !important;
  box-shadow: 0 0 0 2px rgba(52,211,153,0.15) !important;
}

/* ═══ LABELS — flat, no pill background ═══ */
label, .gr-textbox label, .gr-number label,
.gr-dropdown label, .gr-radio label,
.gr-image label, .gr-audio label,
.gr-file label, .gr-checkbox label,
.gradio-container label {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  border-radius: 0 !important;
  color: var(--text-secondary) !important;
  font-size: 0.8rem !important;
  font-weight: 500 !important;
  margin-bottom: 4px !important;
  display: block !important;
}

/* ═══ BUTTONS ═══ */
button.primary, button[class*="primary"],
.gr-button-primary {
  background: linear-gradient(135deg, var(--aa-primary), var(--aa-primary-deep)) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 700 !important;
  padding: 10px 20px !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
}
button.primary:hover, .gr-button-primary:hover {
  filter: brightness(1.1) !important;
  box-shadow: 0 4px 16px rgba(52,211,153,0.3) !important;
}
button.secondary, button[class*="secondary"],
.gr-button-secondary {
  background: var(--bg-3) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-bright) !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
  padding: 10px 20px !important;
}

/* ═══ DROPDOWNS ═══ */
.gr-dropdown select, select {
  background: var(--bg-2) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
}
ul[class*="dropdown"], div[class*="dropdown-arrow"] {
  background: var(--bg-2) !important;
  border: 1px solid var(--border-bright) !important;
}

/* ═══ DATAFRAMES / TABLES ═══ */
table, .dataframe {
  background: var(--bg-1) !important;
  color: var(--text-primary) !important;
  border-collapse: collapse !important;
  width: 100% !important;
}
th {
  background: var(--bg-3) !important;
  color: var(--aa-primary) !important;
  padding: 10px 14px !important;
  font-size: 0.78rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  border-bottom: 1px solid var(--border-bright) !important;
}
td {
  padding: 10px 14px !important;
  border-bottom: 1px solid var(--border) !important;
  font-size: 0.85rem !important;
  color: var(--text-primary) !important;
}
tr:hover td { background: rgba(52,211,153,0.04) !important; }

/* ═══ STATUS BADGES ═══ */
.status-critical { color: var(--aa-danger) !important; font-weight: 700; }
.status-warning  { color: var(--aa-saffron) !important; font-weight: 700; }
.status-stable   { color: var(--aa-primary) !important; font-weight: 700; }

/* ═══ MARKDOWN / OUTPUT ═══ */
.gr-markdown, div[class*="markdown"],
div[class*="output"] {
  background: var(--bg-2) !important;
  color: var(--text-primary) !important;
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border) !important;
  padding: 16px !important;
}

/* ═══ STAT CARDS ═══ */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 20px;
  text-align: center;
  transition: border-color 0.2s, transform 0.2s;
}
.stat-card:hover {
  border-color: var(--aa-primary);
  transform: translateY(-2px);
}
.stat-card .stat-val {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--aa-primary);
  line-height: 1;
  margin-bottom: 6px;
}
.stat-card .stat-lbl {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
}

/* ═══ SECTION HEADERS ═══ */
.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}
.section-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
}
.section-icon {
  width: 32px; height: 32px;
  background: rgba(52,211,153,0.12);
  border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
}

/* ═══ ALERTS ═══ */
.alert-critical {
  background: rgba(248,113,113,0.1);
  border: 1px solid rgba(248,113,113,0.3);
  border-left: 4px solid var(--aa-danger);
  border-radius: var(--radius-sm);
  padding: 12px 16px;
  margin: 8px 0;
  color: var(--text-primary);
}
.alert-warning {
  background: rgba(251,191,36,0.08);
  border: 1px solid rgba(251,191,36,0.25);
  border-left: 4px solid var(--aa-saffron);
  border-radius: var(--radius-sm);
  padding: 12px 16px;
  margin: 8px 0;
  color: var(--text-primary);
}
.alert-ok {
  background: rgba(52,211,153,0.08);
  border: 1px solid rgba(52,211,153,0.25);
  border-left: 4px solid var(--aa-primary);
  border-radius: var(--radius-sm);
  padding: 12px 16px;
  margin: 8px 0;
  color: var(--text-primary);
}

/* ═══ SCROLLBARS ═══ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-0); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ═══ FOOTER ═══ */
.app-footer {
  text-align: center;
  padding: 20px;
  color: var(--text-muted);
  font-size: 0.75rem;
  border-top: 1px solid var(--border);
  margin-top: 32px;
}
.app-footer a { color: var(--aa-primary); text-decoration: none; }
"""
