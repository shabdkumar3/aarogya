from database.schema import get_connection
from datetime import date, timedelta

# ── PATIENTS ──────────────────────────────────────────────

def create_patient(name, age, gender, village, district, language, conditions, allergies):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO patients (name, age, gender, village, district, language, conditions, allergies)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, int(age), gender, village, district or '', language, conditions or '', allergies or ''))
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid

def get_all_patients():
    conn = get_connection()
    rows = conn.cursor().execute("SELECT * FROM patients ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_patient_by_id(patient_id):
    conn = get_connection()
    row = conn.cursor().execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_patient_dropdown_choices():
    patients = get_all_patients()
    return [f"{p['id']}: {p['name']} ({p['village']})" for p in patients]

def parse_dropdown(selection):
    if not selection:
        return None
    try:
        return int(selection.split(":")[0].strip())
    except:
        return None

# ── DIAGNOSES ──────────────────────────────────────────────

def save_diagnosis(patient_id, image_path, symptom_description, raw_response,
                   conditions, urgency, next_steps, red_flags, model_used):
    conn = get_connection()
    conn.cursor().execute("""
        INSERT INTO diagnoses
        (patient_id, image_path, symptom_description, raw_response,
         conditions, urgency, next_steps, red_flags, model_used)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (patient_id, image_path, symptom_description, raw_response,
          conditions, urgency, next_steps, red_flags, model_used))
    conn.commit()
    conn.close()

def get_diagnoses_for_patient(patient_id):
    conn = get_connection()
    rows = conn.cursor().execute(
        "SELECT * FROM diagnoses WHERE patient_id = ? ORDER BY created_at DESC", (patient_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── MEDICATIONS ──────────────────────────────────────────────

def add_medication(patient_id, name, dose, frequency, start_date, end_date=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO medications (patient_id, name, dose, frequency, start_date, end_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (patient_id, name, dose, frequency, start_date, end_date))
    mid = c.lastrowid  # FIX: return the new medication ID
    conn.commit()
    conn.close()
    return mid

def get_active_medications(patient_id):
    conn = get_connection()
    rows = conn.cursor().execute(
        "SELECT * FROM medications WHERE patient_id = ? AND is_active = 1 ORDER BY created_at ASC",
        (patient_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_medications_for_patient(patient_id):
    conn = get_connection()
    rows = conn.cursor().execute(
        "SELECT * FROM medications WHERE patient_id = ? ORDER BY created_at DESC", (patient_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def deactivate_medication(medication_id):
    conn = get_connection()
    conn.cursor().execute("UPDATE medications SET is_active = 0 WHERE id = ?", (medication_id,))
    conn.commit()
    conn.close()

# ── ADHERENCE ──────────────────────────────────────────────

def log_adherence(medication_id, patient_id, log_date, status):
    conn = get_connection()
    conn.cursor().execute("""
        INSERT INTO adherence_logs (medication_id, patient_id, log_date, status)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(medication_id, log_date) DO UPDATE SET status = excluded.status
    """, (medication_id, patient_id, log_date, status))
    conn.commit()
    conn.close()

def get_adherence_last_n_days(patient_id, n=7):
    conn = get_connection()
    since = (date.today() - timedelta(days=n)).isoformat()
    rows = conn.cursor().execute("""
        SELECT al.*, m.name as medication_name, m.dose, m.frequency
        FROM adherence_logs al
        JOIN medications m ON al.medication_id = m.id
        WHERE al.patient_id = ? AND al.log_date >= ?
        ORDER BY al.log_date DESC, m.name ASC
    """, (patient_id, since)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_consecutive_missed(medication_id):
    conn = get_connection()
    rows = conn.cursor().execute("""
        SELECT status FROM adherence_logs
        WHERE medication_id = ?
        ORDER BY log_date DESC LIMIT 14
    """, (medication_id,)).fetchall()
    conn.close()
    count = 0
    for r in rows:
        if r['status'] == 'Missed':
            count += 1
        else:
            break
    return count

def get_7day_adherence_rate(patient_id):
    logs = get_adherence_last_n_days(patient_id, 7)
    if not logs:
        return None
    took = sum(1 for l in logs if l['status'] == 'Took')
    return round((took / len(logs)) * 100)

# ── DASHBOARD ──────────────────────────────────────────────

def get_all_patients_with_status():
    patients = get_all_patients()
    result = []
    for p in patients:
        pid = p['id']
        rate = get_7day_adherence_rate(pid)
        meds = get_active_medications(pid)
        at_risk = any(get_consecutive_missed(m['id']) >= 3 for m in meds)
        diagnoses = get_diagnoses_for_patient(pid)
        last_diag = diagnoses[0]['created_at'][:10] if diagnoses else None
        p['adherence_rate'] = rate
        p['at_risk'] = at_risk
        p['last_diagnosis'] = last_diag
        result.append(p)
    return result
