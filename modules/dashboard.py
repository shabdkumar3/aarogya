from database.queries import get_all_patients_with_status
from llm.client import call_gemma_text
from llm.prompts import HEALTH_TIPS_PROMPT


def get_dashboard_markdown():
    patients = get_all_patients_with_status()
    if not patients:
        return "No patients registered yet. Go to Patient Registry to add patients."

    at_risk = [p for p in patients if p['at_risk']]
    needs_attention = [p for p in patients if not p['at_risk']
                       and p['adherence_rate'] is not None and p['adherence_rate'] < 70]
    stable = [p for p in patients if not p['at_risk']
              and p['adherence_rate'] is not None and p['adherence_rate'] >= 70]
    new_patients = [p for p in patients if p['adherence_rate'] is None]

    lines = [f"### Total Patients: {len(patients)}\n"]

    if at_risk:
        lines.append("## 🔴 At Risk — Follow Up Immediately")
        for p in at_risk:
            last = p['last_diagnosis'] or "No scan"
            lines.append(f"- **{p['name']}** | {p['village']} | Adherence: {p['adherence_rate'] or 'N/A'}% | Last scan: {last}")
        lines.append("")

    if needs_attention:
        lines.append("## 🟡 Needs Attention — Adherence Below 70%")
        for p in needs_attention:
            lines.append(f"- **{p['name']}** | {p['village']} | Adherence: {p['adherence_rate']}%")
        lines.append("")

    if stable:
        lines.append("## 🟢 Stable")
        for p in stable:
            lines.append(f"- **{p['name']}** | {p['village']} | Adherence: {p['adherence_rate']}%")
        lines.append("")

    if new_patients:
        lines.append("## 🆕 New — No Medications Logged")
        for p in new_patients:
            lines.append(f"- **{p['name']}** | {p['village']} | Registered: {p['created_at'][:10]}")

    return "\n".join(lines)


def get_weekly_health_tips(focus_area="seasonal diseases", language="Hindi"):
    prompt = HEALTH_TIPS_PROMPT.format(focus_area=focus_area, language=language)
    tips, _ = call_gemma_text(prompt, temperature=0.7, max_tokens=256)
    return tips or "Could not generate tips."
