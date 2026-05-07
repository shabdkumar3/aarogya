"""
FastAPI REST backend for the Aarogya React frontend.
Run alongside the Gradio app:  uvicorn aarogya.api:app --port 8000
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys, os, base64, tempfile

# Make sure the project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.schema import initialize_database
from database.queries import (
    add_patient, get_all_patients, get_patient_by_id,
    add_medication, get_medications_for_patient,
    log_adherence, get_adherence_logs,
    add_visit, get_visits_for_patient,
)
from llm.client import call_gemma

app = FastAPI(title="Aarogya API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_database()


# ── Schemas ────────────────────────────────────────────────────────────────────

class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    village: str
    phone: Optional[str] = ""
    conditions: Optional[str] = ""
    language: Optional[str] = "English"

class MedicationCreate(BaseModel):
    patient_id: int
    name: str
    dose: str
    frequency: str
    start_date: str
    end_date: Optional[str] = None

class AdherenceLog(BaseModel):
    medication_id: int
    patient_id: int
    date: str
    status: str  # "Took" | "Missed" | "Late"

class VisitCreate(BaseModel):
    patient_id: int
    date: str
    notes: str
    vitals: Optional[str] = ""

class ChatMessage(BaseModel):
    message: str
    language: Optional[str] = "English"
    patient_context: Optional[str] = ""

class DiagnoScanRequest(BaseModel):
    image_b64: Optional[str] = None  # base64 encoded image
    symptoms: str
    language: Optional[str] = "English"


# ── Patients ───────────────────────────────────────────────────────────────────

@app.get("/api/patients")
def list_patients():
    rows = get_all_patients()
    return [dict(r) for r in rows]

@app.get("/api/patients/{patient_id}")
def get_patient(patient_id: int):
    row = get_patient_by_id(patient_id)
    if not row:
        raise HTTPException(status_code=404, detail="Patient not found")
    return dict(row)

@app.post("/api/patients", status_code=201)
def create_patient(body: PatientCreate):
    pid = add_patient(
        body.name, body.age, body.gender, body.village,
        body.phone, body.conditions, body.language
    )
    return {"id": pid, "message": "Patient registered successfully"}


# ── Medications ────────────────────────────────────────────────────────────────

@app.get("/api/patients/{patient_id}/medications")
def list_medications(patient_id: int):
    rows = get_medications_for_patient(patient_id)
    return [dict(r) for r in rows]

@app.post("/api/medications", status_code=201)
def create_medication(body: MedicationCreate):
    mid = add_medication(
        body.patient_id, body.name, body.dose,
        body.frequency, body.start_date, body.end_date
    )
    return {"id": mid, "message": "Medication added successfully"}

@app.post("/api/adherence", status_code=201)
def record_adherence(body: AdherenceLog):
    log_adherence(body.medication_id, body.patient_id, body.date, body.status)
    return {"message": "Adherence logged"}

@app.get("/api/patients/{patient_id}/adherence")
def get_adherence(patient_id: int):
    rows = get_adherence_logs(patient_id)
    return [dict(r) for r in rows]


# ── Visits ─────────────────────────────────────────────────────────────────────

@app.post("/api/visits", status_code=201)
def create_visit(body: VisitCreate):
    add_visit(body.patient_id, body.date, body.notes, body.vitals)
    return {"message": "Visit recorded"}

@app.get("/api/patients/{patient_id}/visits")
def list_visits(patient_id: int):
    rows = get_visits_for_patient(patient_id)
    return [dict(r) for r in rows]


# ── AI Chat ────────────────────────────────────────────────────────────────────

@app.post("/api/chat")
def chat(body: ChatMessage):
    system_prompt = (
        "You are Aarogya, an AI health assistant for rural India. "
        "You help ASHA workers and patients with health guidance. "
        f"Respond in {body.language}. Keep answers concise and practical."
    )
    if body.patient_context:
        system_prompt += f"\n\nPatient context: {body.patient_context}"
    try:
        response = call_gemma(body.message, system_prompt=system_prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── DiagnoScan ─────────────────────────────────────────────────────────────────

@app.post("/api/diagnoscan")
def diagnoscan(body: DiagnoScanRequest):
    prompt = (
        f"A patient reports: {body.symptoms}\n\n"
        "Provide: 1) Likely conditions (triage only), 2) Immediate care steps, "
        "3) Red-flag symptoms requiring urgent referral. "
        f"Respond in {body.language}. Add disclaimer this is not a diagnosis."
    )
    if body.image_b64:
        prompt = f"[Image provided for skin/wound analysis]\n\n{prompt}"
    try:
        response = call_gemma(prompt)
        return {"assessment": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Dashboard stats ────────────────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats():
    from database.queries import get_connection
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total FROM patients")
    total_patients = c.fetchone()[0]
    c.execute("SELECT COUNT(*) as total FROM medications")
    total_meds = c.fetchone()[0]
    c.execute("SELECT COUNT(*) as total FROM adherence_logs WHERE status='Took'")
    took = c.fetchone()[0]
    c.execute("SELECT COUNT(*) as total FROM adherence_logs")
    total_logs = c.fetchone()[0]
    adherence_pct = round((took / total_logs * 100) if total_logs > 0 else 0, 1)
    c.execute("SELECT COUNT(*) as total FROM visits")
    total_visits = c.fetchone()[0]
    conn.close()
    return {
        "total_patients": total_patients,
        "total_medications": total_meds,
        "adherence_percentage": adherence_pct,
        "total_visits": total_visits,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
