"""Patient registration and record display."""
from database.queries import create_patient, get_patient_by_id, get_all_patients

LANGUAGES = ["Hindi", "English", "Tamil", "Telugu", "Bengali", "Marathi"]
GENDERS   = ["Female", "Male", "Other"]


def register_patient(name, age, gender, village, language, phone=""):
    """Register a new patient. Returns (message_str, patient_id_or_None)."""
    errors = []
    if not name or not str(name).strip():
        errors.append("Name is required.")
    try:
        age_int = int(age)
        if not (0 < age_int <= 120):
            errors.append("Age must be between 1 and 120.")
    except (TypeError, ValueError):
        errors.append("Age must be a valid number.")
    if not village or not str(village).strip():
        errors.append("Village is required.")
    if errors:
        return "⚠️ " + " | ".join(errors), None

    try:
        pid = create_patient(
            name=str(name).strip(),
            age=int(age),
            gender=gender or "Other",
            village=str(village).strip(),
            district="",
            language=language or "Hindi",
            conditions="",
            allergies="",
        )
        return f"✅ Patient registered! ID: **{pid}** — {str(name).strip()}", pid
    except Exception as e:
        return f"❌ Registration failed: {e}", None


def format_patient_card(pid):
    """Return a markdown patient card for a given patient ID (int)."""
    if not pid:
        return "*Select a patient to view details.*"
    try:
        p = get_patient_by_id(int(pid))
    except Exception:
        return "*Invalid patient ID.*"
    if not p:
        return "*Patient not found.*"
    return (
        f"**ID:** {p['id']} &nbsp;|&nbsp; **Name:** {p['name']}\n\n"
        f"**Age:** {p['age']} &nbsp;|&nbsp; **Gender:** {p['gender']} "
        f"&nbsp;|&nbsp; **Language:** {p['language']}\n\n"
        f"**Village:** {p['village']}"
        + (f", {p['district']}" if p.get('district') else "") + "\n\n"
        f"**Known Conditions:** {p.get('conditions') or 'None recorded'}\n\n"
        f"**Allergies:** {p.get('allergies') or 'None recorded'}\n\n"
        f"**Registered:** {str(p.get('created_at',''))[:10]}"
    )
