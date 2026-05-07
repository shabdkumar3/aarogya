from database.queries import (
    create_patient, get_all_patients, get_patient_by_id,
    get_patient_dropdown_choices
)

LANGUAGES = ["Hindi", "English", "Tamil", "Telugu", "Bengali"]
GENDERS = ["Male", "Female", "Other"]

def register_patient(name, age, gender, village, district, language, conditions, allergies):
    errors = []
    if not name or not name.strip():
        errors.append("Name is required.")
    try:
        if age is None or not (0 <= int(age) <= 120):
            errors.append("Age must be between 0 and 120.")
    except (TypeError, ValueError):
        errors.append("Age must be a valid number.")
    if not village or not village.strip():
        errors.append("Village is required.")
    if errors:
        return False, " | ".join(errors), None

    pid = create_patient(
        name=name.strip(),
        age=int(age),
        gender=gender,
        village=village.strip(),
        district=(district or "").strip(),
        language=language,
        conditions=(conditions or "").strip(),
        allergies=(allergies or "").strip()
    )
    return True, f"Patient registered successfully. Patient ID: {pid}", pid


def format_patient_card(patient_dropdown_value):
    from database.queries import parse_dropdown
    pid = parse_dropdown(patient_dropdown_value)
    if not pid:
        return "*Select a patient to view details.*"
    p = get_patient_by_id(pid)
    if not p:
        return "Patient not found."
    return f"""
**ID:** {p['id']} | **Name:** {p['name']}
**Age:** {p['age']} | **Gender:** {p['gender']} | **Language:** {p['language']}
**Village:** {p['village']}, {p['district']}
**Conditions:** {p['conditions'] or 'None recorded'}
**Allergies:** {p['allergies'] or 'None recorded'}
**Registered:** {p['created_at'][:10]}
"""
