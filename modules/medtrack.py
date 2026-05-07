import json
from datetime import date
from database.queries import (
    add_medication, get_active_medications, get_all_medications_for_patient,
    log_adherence, get_adherence_last_n_days, get_consecutive_missed,
    parse_dropdown, get_patient_by_id, deactivate_medication
)
from llm.client import call_gemma_with_tools
from llm.prompts import MEDTRACK_ANALYSIS_PROMPT
from llm.tools import MEDTRACK_TOOLS

FREQUENCIES = ["Once daily", "Twice daily", "Three times daily", "Weekly", "SOS / As needed"]


def add_med(patient_dropdown, name, dose, frequency, start_date, end_date):
    pid = parse_dropdown(patient_dropdown)
    if not pid:
        return "Please select a patient."
    if not all([name, dose, frequency, start_date]):
        return "Name, dose, frequency, and start date are all required."
    add_medication(pid, name.strip(), dose.strip(), frequency, start_date, end_date or None)
    return f"'{name}' added successfully."


def stop_med(medication_id_str):
    try:
        mid = int(medication_id_str)
        deactivate_medication(mid)
        return f"Medication ID {mid} marked as completed."
    except:
        return "Invalid medication ID."


def get_active_meds_display(patient_dropdown):
    pid = parse_dropdown(patient_dropdown)
    if not pid:
        return "No patient selected."
    meds = get_active_medications(pid)
    if not meds:
        return "No active medications."
    lines = ["| ID | Name | Dose | Frequency | Since |",
             "|---|---|---|---|---|"]
    for m in meds:
        lines.append(f"| {m['id']} | {m['name']} | {m['dose']} | {m['frequency']} | {m['start_date']} |")
    return "\n".join(lines)


def log_dose(patient_dropdown, medication_id_str, status):
    pid = parse_dropdown(patient_dropdown)
    if not pid:
        return "Please select a patient."
    try:
        mid = int(medication_id_str)
    except:
        return "Invalid medication ID."
    today = date.today().isoformat()
    log_adherence(mid, pid, today, status)
    return f"Logged: {status} for medication ID {mid} on {today}."


def get_adherence_table(patient_dropdown):
    pid = parse_dropdown(patient_dropdown)
    if not pid:
        return "No patient selected."
    logs = get_adherence_last_n_days(pid, 7)
    if not logs:
        return "No adherence records in the last 7 days."
    status_emoji = {"Took": "✅", "Missed": "❌", "Skipped": "⏭️"}
    lines = ["| Date | Medication | Dose | Status |", "|---|---|---|---|"]
    for l in logs:
        e = status_emoji.get(l['status'], "?")
        lines.append(f"| {l['log_date']} | {l['medication_name']} | {l['dose']} | {e} {l['status']} |")
    return "\n".join(lines)


def run_adherence_analysis(patient_dropdown):
    pid = parse_dropdown(patient_dropdown)
    if not pid:
        return "Please select a patient."
    patient = get_patient_by_id(pid)
    meds = get_active_medications(pid)
    if not meds:
        return "No active medications to analyze."

    adherence_data = []
    for m in meds:
        logs = get_adherence_last_n_days(pid, 7)
        med_logs = [l for l in logs if l['medication_id'] == m['id']]
        took = sum(1 for l in med_logs if l['status'] == 'Took')
        adherence_data.append({
            "medication_name": m['name'],
            "dose": m['dose'],
            "frequency": m['frequency'],
            "consecutive_missed_days": get_consecutive_missed(m['id']),
            "took_last_7_days": took,
            "total_logs_last_7_days": len(med_logs)
        })

    prompt = MEDTRACK_ANALYSIS_PROMPT.format(
        patient_name=patient['name'],
        language=patient.get('language', 'Hindi'),
        adherence_json=json.dumps(adherence_data, indent=2)
    )

    result, model_used = call_gemma_with_tools(prompt, MEDTRACK_TOOLS)
    return f"{result}\n\n---\n*Model: {model_used}*"
