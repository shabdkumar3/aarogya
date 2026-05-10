"""Dashboard stats and health tips."""
from database.queries import get_all_patients_with_status
from llm.client import call_gemma_text
from llm.prompts import HEALTH_TIPS_PROMPT


def get_dashboard_markdown():
    """Returns full dashboard markdown string."""
    try:
        patients = get_all_patients_with_status()
    except Exception as e:
        return f"❌ Error loading patients: {e}"

    if not patients:
        return "No patients registered yet. Go to **Patient Registry** to add patients."

    at_risk       = [p for p in patients if p.get("at_risk")]
    low_adherence = [p for p in patients if not p.get("at_risk")
                     and p.get("adherence_rate") is not None
                     and p["adherence_rate"] < 70]
    stable        = [p for p in patients if not p.get("at_risk")
                     and p.get("adherence_rate") is not None
                     and p["adherence_rate"] >= 70]
    new_patients  = [p for p in patients if p.get("adherence_rate") is None]

    lines = [
        f"### 📊 Total Patients: {len(patients)} &nbsp;|&nbsp; "
        f"🔴 At Risk: {len(at_risk)} &nbsp;|&nbsp; "
        f"🟡 Needs Attention: {len(low_adherence)} &nbsp;|&nbsp; "
        f"🟢 Stable: {len(stable)} &nbsp;|&nbsp; "
        f"🆕 New: {len(new_patients)}\n"
    ]

    if at_risk:
        lines.append("## 🔴 At Risk — Follow Up Immediately")
        for p in at_risk:
            last = p.get("last_diagnosis") or "No scan yet"
            lines.append(
                f"- **{p['name']}** | {p['village']} | "
                f"Adherence: {p.get('adherence_rate') or 'N/A'}% | Last scan: {last}"
            )
        lines.append("")

    if low_adherence:
        lines.append("## 🟡 Needs Attention — Adherence Below 70%")
        for p in low_adherence:
            lines.append(
                f"- **{p['name']}** | {p['village']} | Adherence: {p['adherence_rate']}%"
            )
        lines.append("")

    if stable:
        lines.append("## 🟢 Stable")
        for p in stable:
            lines.append(
                f"- **{p['name']}** | {p['village']} | Adherence: {p['adherence_rate']}%"
            )
        lines.append("")

    if new_patients:
        lines.append("## 🆕 New — No Medications Logged Yet")
        for p in new_patients:
            lines.append(
                f"- **{p['name']}** | {p['village']} | "
                f"Registered: {str(p.get('created_at',''))[:10]}"
            )

    return "\n".join(lines)


def get_weekly_health_tips(focus_area="seasonal diseases in rural India", language="Hindi"):
    """Returns (tips_str, model_str)."""
    try:
        prompt = HEALTH_TIPS_PROMPT.format(focus_area=focus_area, language=language)
        tips, model = call_gemma_text(prompt, temperature=0.7, max_tokens=300)
        return tips or "Could not generate tips.", model or "—"
    except Exception as e:
        return f"❌ Could not generate tips: {e}", "error"
