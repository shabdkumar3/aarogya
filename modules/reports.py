"""Generate PDF health summary using ReportLab."""
import os, tempfile
from datetime import date
from database.queries import (
    get_patient_by_id, get_diagnoses_for_patient,
    get_all_medications_for_patient, get_adherence_last_n_days,
)
from llm.client import call_gemma_text
from llm.prompts import PDF_SUMMARY_PROMPT


def generate_patient_pdf(pid):
    """
    Generate PDF for patient. pid = int.
    Returns (file_path_str_or_None, message_str)
    """
    if not pid:
        return None, "⚠️ No patient selected."

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer,
            Table, TableStyle, HRFlowable,
        )
    except ImportError:
        return None, "❌ ReportLab not installed. Run: pip install reportlab"

    try:
        patient = get_patient_by_id(int(pid))
    except Exception as e:
        return None, f"❌ DB error: {e}"

    if not patient:
        return None, "❌ Patient not found."

    try:
        diagnoses     = get_diagnoses_for_patient(int(pid))[:3]
        medications   = get_all_medications_for_patient(int(pid))
        adherence_logs = get_adherence_last_n_days(int(pid), 7)
    except Exception as e:
        return None, f"❌ Error loading patient data: {e}"

    # Build AI summary
    try:
        patient_info_str = (
            f"Name: {patient['name']}, Age: {patient['age']}, "
            f"Gender: {patient['gender']}, Village: {patient['village']}, "
            f"Conditions: {patient.get('conditions') or 'None'}, "
            f"Allergies: {patient.get('allergies') or 'None'}"
        )
        diagnoses_str = "\n".join([
            f"[{str(d.get('created_at',''))[:10]}] Urgency: {d.get('urgency','')}. "
            f"Conditions: {d.get('conditions','')}. Symptoms: {d.get('symptom_description','')}"
            for d in diagnoses
        ]) or "No diagnoses recorded."
        active_meds = [m for m in medications if m.get("is_active")]
        meds_str = "\n".join([
            f"{m['name']} {m['dose']} {m['frequency']} since {m.get('start_date','?')}"
            for m in active_meds
        ]) or "No active medications."
        logs_str = "\n".join([
            f"{l.get('log_date','')}: {l.get('medication_name','')} — {l.get('status','')}"
            for l in adherence_logs
        ]) or "No adherence logs in last 7 days."

        prompt = PDF_SUMMARY_PROMPT.format(
            patient_info=patient_info_str,
            diagnoses=diagnoses_str,
            medications_and_adherence=f"Medications:\n{meds_str}\n\nAdherence:\n{logs_str}",
        )
        ai_summary, _ = call_gemma_text(prompt, temperature=0.1, max_tokens=200)
        ai_summary = ai_summary or "AI summary not available."
    except Exception:
        ai_summary = "AI summary not available."

    # Build PDF
    try:
        safe_name = str(patient["name"]).replace(" ", "_").replace("/", "_")
        tmp = tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=False,
            prefix=f"aarogya_{safe_name}_",
        )
        doc = SimpleDocTemplate(
            tmp.name, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        )
        styles = getSampleStyleSheet()
        story  = []

        story.append(Paragraph("AAROGYA — Patient Health Summary", styles["Title"]))
        story.append(Paragraph(
            f"Generated: {date.today().strftime('%d %B %Y')} | For PHC Doctor Use Only",
            styles["Normal"],
        ))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.green))
        story.append(Spacer(1, 0.3*cm))

        story.append(Paragraph("Patient Information", styles["Heading2"]))
        info_data = [
            ["Name",    patient["name"],                        "Age",      str(patient["age"])],
            ["Gender",  patient["gender"],                      "Village",  patient["village"]],
            ["Language",patient.get("language","Hindi"),        "Registered",str(patient.get("created_at",""))[:10]],
            ["Conditions",patient.get("conditions") or "None", "Allergies",patient.get("allergies") or "None"],
        ]
        tbl = Table(info_data, colWidths=[3*cm, 6*cm, 3*cm, 6*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(0,-1), colors.lightgreen),
            ("BACKGROUND", (2,0),(2,-1), colors.lightgreen),
            ("FONTNAME",   (0,0),(-1,-1),"Helvetica"),
            ("FONTSIZE",   (0,0),(-1,-1), 9),
            ("GRID",       (0,0),(-1,-1), 0.5, colors.grey),
            ("VALIGN",     (0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING", (0,0),(-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.4*cm))

        story.append(Paragraph("AI Clinical Summary", styles["Heading2"]))
        story.append(Paragraph(
            "<i>Auto-generated by Aarogya. Not a substitute for clinical assessment.</i>",
            styles["Normal"],
        ))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(ai_summary, styles["Normal"]))
        story.append(Spacer(1, 0.4*cm))

        if diagnoses:
            story.append(Paragraph("Recent Triage (Last 3)", styles["Heading2"]))
            for d in diagnoses:
                story.append(Paragraph(
                    f"<b>{str(d.get('created_at',''))[:10]}</b> — "
                    f"Urgency: {d.get('urgency','')} | Conditions: {d.get('conditions','')}",
                    styles["Normal"],
                ))
                story.append(Paragraph(f"Symptoms: {d.get('symptom_description','')}", styles["Normal"]))
                story.append(Spacer(1, 0.2*cm))

        if active_meds:
            story.append(Paragraph("Active Medications", styles["Heading2"]))
            med_data = [["Medication","Dose","Frequency","Since"]]
            for m in active_meds:
                med_data.append([m["name"], m["dose"], m["frequency"], m.get("start_date","?")])
            med_tbl = Table(med_data, colWidths=[5*cm,3*cm,4*cm,4*cm])
            med_tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0), colors.green),
                ("TEXTCOLOR", (0,0),(-1,0), colors.white),
                ("FONTNAME",  (0,0),(-1,0), "Helvetica-Bold"),
                ("FONTSIZE",  (0,0),(-1,-1), 9),
                ("GRID",      (0,0),(-1,-1), 0.5, colors.grey),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.lightgrey]),
            ]))
            story.append(med_tbl)
            story.append(Spacer(1, 0.4*cm))

        if adherence_logs:
            story.append(Paragraph("7-Day Adherence Log", styles["Heading2"]))
            adh_data = [["Date","Medication","Status"]]
            for l in adherence_logs:
                adh_data.append([l.get("log_date",""), l.get("medication_name",""), l.get("status","")])
            adh_tbl = Table(adh_data, colWidths=[4*cm,8*cm,4*cm])
            adh_tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0), colors.green),
                ("TEXTCOLOR", (0,0),(-1,0), colors.white),
                ("FONTNAME",  (0,0),(-1,0), "Helvetica-Bold"),
                ("FONTSIZE",  (0,0),(-1,-1), 9),
                ("GRID",      (0,0),(-1,-1), 0.5, colors.grey),
            ]))
            story.append(adh_tbl)

        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
        story.append(Paragraph(
            "Aarogya is an AI triage support tool. All findings must be verified by a qualified clinician.",
            styles["Normal"],
        ))

        doc.build(story)
        return tmp.name, f"✅ PDF generated for {patient['name']}"

    except Exception as e:
        return None, f"❌ PDF generation failed: {e}"
