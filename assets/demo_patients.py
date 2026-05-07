"""
Seeds the database with 4 demo patients covering all dashboard states.
Run ONCE before recording the demo video:
    python assets/demo_patients.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.schema import initialize_database
from database.queries import create_patient, add_medication, log_adherence
from datetime import date, timedelta


def seed():
    initialize_database()
    print("Seeding demo patients...")

    # ── Patient 1: Ramesh — AT RISK ──────────────────────────────────
    p1 = create_patient(
        name="Ramesh Kumar", age=52, gender="Male",
        village="Mandawa", district="Jhunjhunu", language="Hindi",
        conditions="Type 2 Diabetes, Hypertension", allergies="None"
    )
    m1a = add_medication(p1, "Metformin", "500mg", "Twice daily", "2026-04-01")
    m1b = add_medication(p1, "Amlodipine", "5mg", "Once daily", "2026-04-01")

    # Took for 4 days, missed last 4 days → AT RISK
    for i in range(8):
        d = (date.today() - timedelta(days=7 - i)).isoformat()
        log_adherence(m1a, p1, d, "Took" if i < 4 else "Missed")
        log_adherence(m1b, p1, d, "Took")

    print(f"  Ramesh Kumar (ID: {p1}) — AT RISK (missed Metformin 4 days)")

    # ── Patient 2: Sunita — STABLE ───────────────────────────────────
    p2 = create_patient(
        name="Sunita Devi", age=34, gender="Female",
        village="Barmer", district="Barmer", language="Hindi",
        conditions="Tuberculosis (on DOTS therapy)", allergies="Sulpha drugs"
    )
    m2 = add_medication(p2, "HRZE DOTS Regimen", "4 tablets", "Once daily", "2026-03-01", "2026-08-31")

    for i in range(7):
        d = (date.today() - timedelta(days=6 - i)).isoformat()
        log_adherence(m2, p2, d, "Took")

    print(f"  Sunita Devi (ID: {p2}) — STABLE (perfect adherence)")

    # ── Patient 3: Lakshmi — NEEDS ATTENTION ─────────────────────────
    p3 = create_patient(
        name="Lakshmi Bai", age=67, gender="Female",
        village="Kota Rural", district="Kota", language="Hindi",
        conditions="Arthritis, Hypertension", allergies="Aspirin"
    )
    m3 = add_medication(p3, "Losartan", "50mg", "Once daily", "2026-04-10")

    statuses = ["Took", "Took", "Missed", "Took", "Skipped", "Missed", "Took"]
    for i, status in enumerate(statuses):
        d = (date.today() - timedelta(days=6 - i)).isoformat()
        log_adherence(m3, p3, d, status)

    print(f"  Lakshmi Bai (ID: {p3}) — NEEDS ATTENTION (57% adherence)")

    # ── Patient 4: Arjun — NEW ────────────────────────────────────────
    p4 = create_patient(
        name="Arjun Singh", age=28, gender="Male",
        village="Jaipur Rural", district="Jaipur", language="Hindi",
        conditions="None", allergies="None"
    )
    print(f"  Arjun Singh (ID: {p4}) — NEW (no medications)")

    print("\nDemo data seeded. Dashboard shows: 1 At Risk, 1 Stable, 1 Needs Attention, 1 New")


if __name__ == "__main__":
    seed()
