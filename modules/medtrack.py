"""Medication tracking and adherence analysis."""
import json
from datetime import date, timedelta
from database.queries import (
    add_medication, get_active_medications, get_all_medications_for_patient,
    log_adherence, get_adherence_last_n_days, get_consecutive_missed,
    get_patient_by_id, deactivate_medication,
)
from llm.client import call_gemma_with_tools
from llm.prompts import MEDTRACK_ANALYSIS_PROMPT
from llm.tools import MEDTRACK_TOOLS

FREQUENCIES = ["Once daily", "Twice daily", "Three times daily", "Weekly", "SOS / As needed"]


def add_med(pid, name, dosage, frequency, duration_days, notes=""):
    """Add a medication. pid=int, duration_days=int. Returns status string."""
    if not pid:
        return "⚠️ No patient selected."
    if not name or not str(name).strip():
        return "⚠️ Medicine name is required."
    if not dosage or not str(dosage).strip():
        return "⚠️ Dosage is required."
    try:
        dur = max(1, int(duration_days))
    except (TypeError, ValueError):
        dur = 7
    start = date.today().isoformat()
    end   = (date.today() + timedelta(days=dur)).isoformat()
    note_str = str(notes).strip() if notes else ""
    full_dosage = f"{dosage}" + (f" ({note_str})" if note_str else "")
    try:
        mid = add_medication(int(pid), str(name).strip(), full_dosage, frequency, start, end)
        return f"✅ **{name}** added (ID: {mid}) — {frequency} for {dur} days."
    except Exception as e:
        return f"❌ Failed to add medication: {e}"


def stop_med(med_id):
    """Stop a medication by ID. Returns status string."""
    try:
        mid = int(med_id)
        if mid <= 0:
            return "⚠️ Enter a valid medication ID."
        deactivate_medication(mid)
        return f"✅ Medication ID {mid} marked as completed."
    except (TypeError, ValueError):
        return "⚠️ Invalid medication ID — must be a number."
    except Exception as e:
        return f"❌ Error: {e}"


def get_active_meds_display(pid):
    """Returns markdown table of active meds. pid=int."""
    if not pid:
        return "*No patient selected.*"
    try:
        meds = get_active_medications(int(pid))
    except Exception as e:
        return f"*Error loading medications: {e}*"
    if not meds:
        return "*No active medications for this patient.*"
    lines = ["| ID | Medicine | Dosage | Frequency | Since | Until |",
             "|---|---|---|---|---|---|"]
    for m in meds:
        lines.append(
            f"| {m['id']} | {m['name']} | {m['dose']} | {m['frequency']} "
            f"| {m.get('start_date','?')} | {m.get('end_date','?')} |"
        )
    return "\n".join(lines)


def log_dose(med_id, taken, notes=""):
    """
    Log a dose. taken=bool. Returns status string.
    med_id: int
    """
    try:
        mid = int(med_id)
        if mid <= 0:
            return "⚠️ Enter a valid medication ID."
    except (TypeError, ValueError):
        return "⚠️ Invalid medication ID."

    # Look up patient_id from medication
    try:
        from database.schema import get_connection
        conn = get_connection()
        row  = conn.cursor().execute(
            "SELECT patient_id FROM medications WHERE id = ?", (mid,)
        ).fetchone()
        conn.close()
        if not row:
            return f"⚠️ Medication ID {mid} not found."
        patient_id = row["patient_id"]
    except Exception as e:
        return f"❌ DB error: {e}"

    status = "Took" if taken else "Missed"
    today  = date.today().isoformat()
    try:
        log_adherence(mid, patient_id, today, status)
        note_str = f" — {notes}" if notes and str(notes).strip() else ""
        return f"✅ Logged: **{status}** for Med ID {mid} on {today}{note_str}"
    except Exception as e:
        return f"❌ Failed to log dose: {e}"


def get_adherence_table(pid):
    """Returns list-of-lists for Gradio Dataframe. pid=int."""
    if not pid:
        return []
    try:
        logs = get_adherence_last_n_days(int(pid), 14)
    except Exception:
        return []
    if not logs:
        return []
    rows = []
    status_icons = {"Took": "✅ Took", "Missed": "❌ Missed", "Skipped": "⏭️ Skipped"}
    for l in logs:
        rows.append([
            l.get("log_date", ""),
            l.get("medication_name", ""),
            l.get("dose", ""),
            status_icons.get(l.get("status", ""), l.get("status", "")),
        ])
    return rows


def run_adherence_analysis(pid):
    """Run AI adherence analysis. Returns (result_str, model_str)."""
    if not pid:
        return "⚠️ No patient selected.", "—"
    try:
        patient = get_patient_by_id(int(pid))
        if not patient:
            return "⚠️ Patient not found.", "—"
        meds = get_active_medications(int(pid))
        if not meds:
            return "ℹ️ No active medications to analyze.", "—"

        adherence_data = []
        for m in meds:
            logs     = get_adherence_last_n_days(int(pid), 7)
            med_logs = [l for l in logs if l.get("medication_id") == m["id"]]
            took     = sum(1 for l in med_logs if l.get("status") == "Took")
            adherence_data.append({
                "medication_name":          m["name"],
                "dose":                     m["dose"],
                "frequency":                m["frequency"],
                "consecutive_missed_days":  get_consecutive_missed(m["id"]),
                "took_last_7_days":         took,
                "total_logs_last_7_days":   len(med_logs),
            })

        prompt = MEDTRACK_ANALYSIS_PROMPT.format(
            patient_name=patient["name"],
            language=patient.get("language", "Hindi"),
            adherence_json=json.dumps(adherence_data, indent=2, ensure_ascii=False),
        )
        result, model_used = call_gemma_with_tools(prompt, MEDTRACK_TOOLS)
        return (result or "No analysis generated."), model_used

    except Exception as e:
        return f"❌ Analysis failed: {e}", "error"
