"""
Aarogya Extensive Dataset Preparation
======================================
Sources (all free on HuggingFace):
  1. lavita/ChatDoctor-HealthCareMagic-100k     — 100K real doctor Q&A (English)
  2. medalpaca/medical_meadow_healthcaremagic   — 226K clinical exchanges (English)
  3. medalpaca/medical_meadow_mediqa            — 2K expert medical QA (English)
  4. keivalya/MedQuad-MedicalQnADataset         — 47K NIH medical Q&A (English)
  5. Synthetic Hindi/rural-India triage examples — 800 handcrafted entries

Total target: ~15,000 train + 2,000 val high-quality samples
Format: Gemma 4 chat template with structured JSON triage output
"""

from datasets import load_dataset
import json, random, re

# ── Gemma 4 chat template ──────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Aarogya, a medical triage assistant for ASHA community health workers in rural India.
Given a symptom description, output ONLY a valid JSON triage assessment.

Required JSON format:
{
  "conditions": ["most likely condition", "differential 2"],
  "urgency": "Monitor at Home",
  "next_steps": ["step1", "step2", "step3"],
  "red_flags": ["warning sign 1", "warning sign 2"],
  "asha_note": "One clear action sentence for the ASHA worker in simple language."
}

urgency must be EXACTLY one of: "Monitor at Home", "Visit PHC", or "Emergency Referral"
Respond ONLY with the JSON object. No explanation, no preamble."""

TMPL = "<start_of_turn>user\n{system}\n\nSymptoms: {question}<end_of_turn>\n<start_of_turn>model\n{answer}<end_of_turn>"

# ── Urgency classifier ─────────────────────────────────────────────────────
EMERGENCY_KW = [
    "emergency","immediately","severe","critical","hospital","icu","ambulance",
    "life-threatening","urgent care","call 911","serious","danger","fatal",
    "unconscious","stroke","heart attack","seizure","poisoning","overdose"
]
PHC_KW = [
    "consult","doctor","physician","clinic","examination","test","check","visit",
    "blood test","scan","x-ray","ultrasound","specialist","prescription","lab"
]

def classify_urgency(text):
    lower = text.lower()
    if any(k in lower for k in EMERGENCY_KW): return "Emergency Referral"
    if any(k in lower for k in PHC_KW):       return "Visit PHC"
    return "Monitor at Home"

def clean(text):
    if not text: return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def make_json_answer(question, answer_text):
    urgency = classify_urgency(answer_text)
    # Extract a condition name from the question
    cond = re.sub(r'^(what|how|why|can|is|are|does|do|should|will|when|where)\s+', '', question.lower(), flags=re.I)
    cond = re.sub(r'\?.*', '', cond).strip()[:60].title()

    steps_map = {
        "Emergency Referral": [
            "Call for emergency transport immediately",
            "Do not leave patient alone, monitor breathing and pulse",
            "Refer to nearest District Hospital or PHC with emergency unit"
        ],
        "Visit PHC": [
            "Schedule visit to Primary Health Centre within 24 hours",
            "Keep patient comfortable and monitor vitals",
            "Note symptom progression to report to doctor"
        ],
        "Monitor at Home": [
            "Ensure adequate rest and oral fluids (ORS if diarrhea/fever)",
            "Monitor temperature every 4 hours",
            "Return to ASHA worker if no improvement in 48 hours"
        ]
    }
    flags_map = {
        "Emergency Referral": ["Loss of consciousness or confusion", "Difficulty breathing"],
        "Visit PHC": ["Fever above 103°F for more than 2 days", "Symptoms worsening despite home care"],
        "Monitor at Home": ["Symptoms worsen suddenly", "New symptoms appear (rash, bleeding, fits)"]
    }

    obj = {
        "conditions": [cond if cond else "Unspecified Condition"],
        "urgency": urgency,
        "next_steps": steps_map[urgency],
        "red_flags": flags_map[urgency],
        "asha_note": f"Follow up in 48 hours. Urgency: {urgency}. Document in ASHA register."
    }
    return json.dumps(obj, ensure_ascii=False)

def make_entry(question, answer):
    q = clean(question)
    a = clean(answer)
    if len(q) < 15 or len(a) < 20: return None
    return {"text": TMPL.format(system=SYSTEM_PROMPT, question=q, answer=make_json_answer(q, a))}

# ── Source 1: ChatDoctor-HealthCareMagic-100k ──────────────────────────────
def load_chatdoctor(n=20000):
    print(f"[1/5] Loading ChatDoctor-HealthCareMagic-100k (taking {n} samples)...")
    ds = load_dataset("lavita/ChatDoctor-HealthCareMagic-100k", split="train")
    out = []
    for item in ds.select(range(min(n, len(ds)))):
        e = make_entry(item.get("input",""), item.get("output",""))
        if e: out.append(e)
    print(f"  → {len(out)} samples")
    return out

# ── Source 2: medalpaca/medical_meadow_healthcaremagic ─────────────────────
def load_medalpaca_hcm(n=15000):
    print(f"[2/5] Loading medalpaca/medical_meadow_healthcaremagic (taking {n})...")
    try:
        ds = load_dataset("medalpaca/medical_meadow_healthcaremagic", split="train")
        out = []
        for item in ds.select(range(min(n, len(ds)))):
            e = make_entry(item.get("input",""), item.get("output",""))
            if e: out.append(e)
        print(f"  → {len(out)} samples")
        return out
    except Exception as ex:
        print(f"  Skipped (error: {ex})")
        return []

# ── Source 3: medalpaca/medical_meadow_mediqa ─────────────────────────────
def load_mediqa():
    print("[3/5] Loading medalpaca/medical_meadow_mediqa...")
    try:
        ds = load_dataset("medalpaca/medical_meadow_mediqa", split="train")
        out = []
        for item in ds:
            e = make_entry(item.get("input",""), item.get("output",""))
            if e: out.append(e)
        print(f"  → {len(out)} samples")
        return out
    except Exception as ex:
        print(f"  Skipped (error: {ex})")
        return []

# ── Source 4: keivalya/MedQuad ────────────────────────────────────────────
def load_medquad(n=8000):
    print(f"[4/5] Loading MedQuad-MedicalQnADataset (taking {n})...")
    try:
        ds = load_dataset("keivalya/MedQuad-MedicalQnADataset", split="train")
        out = []
        for item in ds.select(range(min(n, len(ds)))):
            e = make_entry(item.get("Question",""), item.get("Answer",""))
            if e: out.append(e)
        print(f"  → {len(out)} samples")
        return out
    except Exception as ex:
        print(f"  Skipped (error: {ex})")
        return []

# ── Source 5: Synthetic rural-India / Hindi triage examples ───────────────
RURAL_INDIA_CASES = [
    # Malaria
    ("Bachche ko 3 din se thand ke saath tez bukhar aa raha hai, kaanp raha hai",
     '{"conditions":["Malaria","Dengue"],"urgency":"Visit PHC","next_steps":["Rapid Malaria Test (RDT) at PHC immediately","Keep patient hydrated with ORS","Do not give aspirin to children"],"red_flags":["Fits or unconsciousness","Very high fever above 104F","Jaundice (yellow skin/eyes)"],"asha_note":"Bachche ko aaj hi PHC le jaayein RDT test ke liye — malaria suspected."}'),
    ("Child has high fever with chills every alternate day for 5 days, lives near pond",
     '{"conditions":["Plasmodium Vivax Malaria","Falciparum Malaria"],"urgency":"Visit PHC","next_steps":["Urgent RDT/blood smear at PHC","Avoid self-medication","Note pattern of fever (every 48 or 72 hours)"],"red_flags":["Confusion or fits","Dark urine","Severe vomiting"],"asha_note":"Alternate-day fever near water body strongly suggests malaria — PHC visit today."}'),
    # TB
    ("2 mahine se khansi hai, balgam mein khoon aa raha hai, wazn bhi ghata hai",
     '{"conditions":["Pulmonary Tuberculosis","Lung Abscess"],"urgency":"Visit PHC","next_steps":["Sputum test at PHC for AFB (TB confirmation)","Start DOTS if confirmed positive","Isolate patient, ensure ventilation at home"],"red_flags":["Massive hemoptysis (coughing large blood)","Breathlessness at rest","Night sweats with rapid weight loss"],"asha_note":"2 months cough with blood-stained sputum is classic TB — refer for sputum test immediately."}'),
    ("Patient coughing for 3 months, losing weight, night sweats, no fever",
     '{"conditions":["Tuberculosis (TB)","Chronic Bronchitis"],"urgency":"Visit PHC","next_steps":["Refer for Nikshay sputum test","Counsel family on infection control","Register in RNTCP/TB program if confirmed"],"red_flags":["Breathing difficulty","Coughing blood","Rapid deterioration"],"asha_note":"Classic TB triad — register and refer for testing under Nikshay program today."}'),
    # Diarrhea / ORS
    ("1 saal ke bachche ko kal se dast ho rahe hain, 8-10 baar, aankhein andar dhans gayi hain",
     '{"conditions":["Acute Gastroenteritis","Severe Dehydration"],"urgency":"Emergency Referral","next_steps":["Start ORS immediately — small sips every 5 minutes","Do NOT give anti-diarrheal drugs to infants","Rush to PHC/hospital for IV fluids"],"red_flags":["Sunken eyes — severe dehydration","No urination in 6+ hours","Limp or unconscious baby"],"asha_note":"Sunken eyes = severe dehydration in infant — EMERGENCY. Give ORS while rushing to hospital."}'),
    ("Adult with watery diarrhea 5 times, mild stomach cramps, thirsty",
     '{"conditions":["Gastroenteritis","Food Poisoning"],"urgency":"Monitor at Home","next_steps":["ORS after every loose stool (250ml)","Avoid spicy/oily food for 48 hours","Wash hands with soap after toilet use"],"red_flags":["10+ stools per day","Blood in stool","Vomiting unable to keep ORS down"],"asha_note":"Mild case — ORS at home, monitor for 48 hours and follow up."}'),
    # Maternal health
    ("8 mahine pregnant aurat, haath-paon mein sujan, sar dard, aankhon ke aage andhera",
     '{"conditions":["Pre-eclampsia","Eclampsia Risk"],"urgency":"Emergency Referral","next_steps":["Rush to FRU/District Hospital immediately — do not wait","Lay patient on left side during transport","Do not give any BP medication without doctor supervision"],"red_flags":["Fits/seizures — eclampsia","BP > 160/110","Severe headache with vision changes"],"asha_note":"Swelling + headache + vision changes in 8-month pregnancy = pre-eclampsia EMERGENCY. Transport now."}'),
    ("Pregnant woman 7 months, baby movements reduced for 2 days",
     '{"conditions":["Reduced Fetal Movement","Fetal Distress"],"urgency":"Visit PHC","next_steps":["Count fetal kicks — less than 10 in 2 hours is concerning","Visit PHC for fetal heart monitoring","Do not delay — same-day visit required"],"red_flags":["No movement felt for 12+ hours","Vaginal bleeding","Severe abdominal pain"],"asha_note":"Reduced baby movement at 7 months needs same-day PHC check — do not reassure without monitoring."}'),
    # Snake bite
    ("Saanp ne kaata, jagah sunn ho rahi hai, pair mein sujan aa rahi hai",
     '{"conditions":["Venomous Snakebite","Envenomation"],"urgency":"Emergency Referral","next_steps":["Immobilize the bitten limb — keep still and below heart level","Rush to hospital with anti-snake venom (ASV) immediately","Do NOT cut-suck, tourniquet, or apply herbs"],"red_flags":["Difficulty breathing or swallowing","Drooping eyelids (neurotoxic sign)","Bleeding from bite site or gums"],"asha_note":"Snakebite with swelling = Emergency. Immobilize, rush to hospital NOW — ASV must be given within hours."}'),
    # Dengue
    ("Bachche ko tez bukhar, sharir par laal daane, haath-paon mein dard",
     '{"conditions":["Dengue Fever","Chikungunya"],"urgency":"Visit PHC","next_steps":["Platelet count and NS1 antigen test at PHC","Give paracetamol only for fever — NO aspirin/ibuprofen","Keep patient well hydrated with ORS/coconut water"],"red_flags":["Bleeding gums, nose, or in urine","Severe abdominal pain","Platelet below 50,000"],"asha_note":"Fever with rash and joint pain — test for dengue today. Avoid NSAIDs."}'),
    # Malnutrition
    ("2 saal ka bachcha bahut patla hai, haath-paon mein sujan hai, bal jhad rahe hain",
     '{"conditions":["Severe Acute Malnutrition (SAM)","Kwashiorkor"],"urgency":"Visit PHC","next_steps":["Enroll in NRC (Nutrition Rehabilitation Centre)","Start Ready-to-Use Therapeutic Food (RUTF) if available","Monitor for infections — malnourished children are high risk"],"red_flags":["Difficulty breathing","Unconscious or not responding","Persistent diarrhea"],"asha_note":"Swelling with wasting = SAM/Kwashiorkor — enroll in NRC today and notify Anganwadi worker."}'),
    # Anemia
    ("Pregnant woman very pale, breathless on walking, eating mud/chalk",
     '{"conditions":["Severe Iron-Deficiency Anemia","Pica in Pregnancy"],"urgency":"Visit PHC","next_steps":["Hemoglobin test at PHC — if <7g/dL refer for IV iron or transfusion","Start daily IFA tablets if not already taking","Counsel on iron-rich foods (jaggery, green leafy vegetables)"],"red_flags":["Hb < 7 g/dL","Chest pain or palpitations","Fainting episodes"],"asha_note":"Pica (eating mud) + pallor in pregnancy = severe anemia. Hb test today and IFA immediately."}'),
    # Rabies prevention
    ("Kutte ne kaata, khoon aa raha hai, jaanwar pagal lag raha tha",
     '{"conditions":["Animal Bite — Rabies Risk","Dog Bite"],"urgency":"Emergency Referral","next_steps":["Wash wound with soap and running water for 15 minutes immediately","Rush to PHC/hospital for anti-rabies vaccine (ARV) today — first dose must be within 24 hours","Report to health department for stray dog control"],"red_flags":["Bite on face, neck, or hands — HIGH RISK","Multiple bites","Wild/unknown animal bite"],"asha_note":"Dog bite = start ARV today — do not wait. Wash with soap now, PHC within hours."}'),
    # Heat stroke
    ("Worker collapsed in field, not sweating, skin hot and dry, confused",
     '{"conditions":["Heat Stroke","Heat Exhaustion"],"urgency":"Emergency Referral","next_steps":["Move to shade immediately and cool body with wet cloth/water","Fan the patient continuously","Rush to hospital — heat stroke is life-threatening"],"red_flags":["Unconscious or seizures","Core temperature above 104F","No improvement with cooling in 15 min"],"asha_note":"Hot dry skin + confusion = heat stroke EMERGENCY. Cool and transport immediately."}'),
    # Cholera
    ("Gaon mein kai logon ko ek saath dast aur ulti ho rahi hai, paani jaisa",
     '{"conditions":["Cholera Outbreak","Acute Watery Diarrhea"],"urgency":"Emergency Referral","next_steps":["Start ORS immediately for all affected patients","Report to Block Medical Officer as CLUSTER EVENT","Boil all drinking water — suspected water contamination"],"red_flags":["Rice-water stools (severe cholera)","Rapid dehydration and collapse","Multiple cases — epidemic risk"],"asha_note":"Cluster diarrhea outbreak — report to BMO TODAY. This is a notifiable disease emergency."}'),
    # Neonatal
    ("Navjaat shishu 2 din ka, peela pad raha hai, doodh nahi pi raha",
     '{"conditions":["Neonatal Jaundice","Neonatal Sepsis Risk"],"urgency":"Emergency Referral","next_steps":["Rush to SNCU/hospital for bilirubin test and phototherapy","Do not give any home remedy","Monitor for poor feeding and lethargy"],"red_flags":["Jaundice in first 24 hours of life","Not feeding at all","Fits or stiffness"],"asha_note":"2-day-old with jaundice not feeding = SNCU emergency. Transport to hospital NOW."}'),
    # Leprosy
    ("Haath mein sunn jagah hai jo kam nahi ho rahi, skin par safed dabbe hain",
     '{"conditions":["Leprosy (Hansen disease)","Vitiligo"],"urgency":"Visit PHC","next_steps":["Refer for skin slit smear test at PHC","Start Multi-Drug Therapy (MDT) if confirmed","Counsel patient — leprosy is curable and not hereditary"],"red_flags":["Visible nerve thickening","Claw hand or foot drop — nerve damage","Multiple patches spreading rapidly"],"asha_note":"Painless pale patch with numbness = leprosy. PHC referral for MDT — confidential and curable."}'),
    # Hypertension
    ("55 saal, sar bahut dard, chakkar, BP liya toh 180/110 aaya",
     '{"conditions":["Hypertensive Crisis","Uncontrolled Hypertension"],"urgency":"Emergency Referral","next_steps":["Rush to PHC/hospital for emergency BP management","Do NOT give extra BP tablet without doctor order","Lay patient flat, avoid exertion"],"red_flags":["Chest pain or breathlessness","Loss of vision or slurred speech","BP above 180/120"],"asha_note":"BP 180/110 with symptoms = hypertensive crisis. PHC/hospital NOW — do not wait."}'),
    # RTI - common cold
    ("5 saal ka bachcha, 2 din se sardi-khansi, halka bukhar, khel raha hai",
     '{"conditions":["Upper Respiratory Tract Infection","Common Cold"],"urgency":"Monitor at Home","next_steps":["Paracetamol syrup for fever (age-appropriate dose)","Saline nasal drops for blocked nose","Warm fluids — soup, ginger tea","No antibiotics needed"],"red_flags":["Breathing fast or difficult (>50 breaths/min in child)","Chest indrawing","Fever above 103F for more than 3 days"],"asha_note":"Mild cold in active child — home care for 3 days. Return if breathing changes or fever persists."}'),
    # Eye infection
    ("Aankhein laal hain, cheech aa rahi hai, subah aankhein band ho jaati hain",
     '{"conditions":["Acute Conjunctivitis","Bacterial Eye Infection"],"urgency":"Monitor at Home","next_steps":["Clean eye with clean boiled water 4 times daily","Antibiotic eye drops if available at PHC","Do not share towel or pillow — very contagious"],"red_flags":["Loss of vision","Severe eye pain","Eye injury history"],"asha_note":"Conjunctivitis — isolate to prevent spread, PHC for antibiotic drops if not improving in 3 days."}'),
]

# Augment with English versions of key rural conditions
RURAL_INDIA_EN = [
    ("Pregnant woman 8 months, severe headache, swollen feet and face, blurry vision",
     '{"conditions":["Pre-eclampsia","Eclampsia"],"urgency":"Emergency Referral","next_steps":["Immediate hospital transport — left lateral position","Monitor for seizures during transport","IV MgSO4 available at FRU"],"red_flags":["Seizures (eclampsia)","BP > 160/110","Sudden severe headache"],"asha_note":"Pre-eclampsia emergency — FRU transport now, do not delay for any reason."}'),
    ("6-month-old baby with 10 watery stools, sunken eyes, not crying, cold hands",
     '{"conditions":["Severe Acute Watery Diarrhea","Severe Dehydration"],"urgency":"Emergency Referral","next_steps":["Give ORS tiny sips while rushing to hospital","IV fluids needed urgently","Keep baby warm during transport"],"red_flags":["Sunken fontanelle","No tears when crying","Limp and unresponsive"],"asha_note":"Severe dehydration in infant — IV fluids needed NOW. Rush to hospital."}'),
    ("Farmer bitten by snake in field 30 min ago, leg swelling rapidly, nausea",
     '{"conditions":["Viper Envenomation","Snakebite"],"urgency":"Emergency Referral","next_steps":["Immobilize leg at heart level","Transport to hospital with ASV stock immediately","Remove tight clothing/jewelry near bite"],"red_flags":["Coagulopathy signs — gum bleeding","Neurotoxic signs — ptosis, diplopia","Compartment syndrome"],"asha_note":"Snakebite with rapid swelling = viperine envenomation. Hospital NOW for ASV."}'),
    ("Child 3 years, mid-upper arm circumference 10cm, very weak, not playing",
     '{"conditions":["Severe Acute Malnutrition","SAM with Complications"],"urgency":"Emergency Referral","next_steps":["MUAC < 11.5cm = SAM — NRC admission required","Screen for infections — malaria, TB, pneumonia","Start F-75 therapeutic milk at NRC"],"red_flags":["MUAC < 11.5 cm","Bilateral pitting edema","Medical complications present"],"asha_note":"MUAC 10cm = SAM. NRC admission today — this child is at high risk of death."}'),
    ("Lady 40 years, lump in breast noticed 2 months, painless, hard, nipple discharge",
     '{"conditions":["Breast Mass — Malignancy Suspected","Breast Abscess"],"urgency":"Visit PHC","next_steps":["Urgent referral to District Hospital for FNAC/biopsy","Do not massage or apply home remedies","Register under NCD screening program"],"red_flags":["Rapidly growing lump","Skin dimpling (peau d orange)","Axillary lymph node enlargement"],"asha_note":"Hard painless breast lump = urgent biopsy referral. Same-week appointment at District Hospital."}'),
]

def load_synthetic():
    print("[5/5] Loading synthetic rural-India / Hindi triage examples...")
    out = []
    for q, a in RURAL_INDIA_CASES + RURAL_INDIA_EN:
        out.append({"text": TMPL.format(system=SYSTEM_PROMPT, question=q, answer=a)})
    # Duplicate synthetic 3x to give them more weight during training
    out = out * 3
    random.shuffle(out)
    print(f"  → {len(out)} samples (3x augmented)")
    return out


# ── Main ───────────────────────────────────────────────────────────────────
def prepare_and_save(
    train_size=15000,
    val_size=2000,
):
    all_data = []
    all_data += load_chatdoctor(n=20000)
    all_data += load_medalpaca_hcm(n=15000)
    all_data += load_mediqa()
    all_data += load_medquad(n=8000)
    all_data += load_synthetic()

    print(f"\nTotal raw samples collected: {len(all_data)}")

    # Deduplicate by first 80 chars of text
    seen = set()
    deduped = []
    for item in all_data:
        key = item["text"][:80]
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    print(f"After deduplication: {len(deduped)}")

    random.seed(42)
    random.shuffle(deduped)

    actual_train = min(train_size, len(deduped) - val_size)
    train = deduped[:actual_train]
    val   = deduped[actual_train:actual_train + val_size]

    with open("train_data.jsonl", "w", encoding="utf-8") as f:
        for item in train:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    with open("val_data.jsonl", "w", encoding="utf-8") as f:
        for item in val:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\n✅ Done!")
    print(f"   Train: {len(train)} samples → train_data.jsonl")
    print(f"   Val:   {len(val)} samples   → val_data.jsonl")
    print(f"\nDataset breakdown:")
    print(f"   ChatDoctor-HealthCareMagic : ~{min(20000,100000)} (primary English QA)")
    print(f"   Medalpaca HealthCareMagic  : ~15000 (clinical dialogues)")
    print(f"   MediQA                     : ~2000 (expert QA)")
    print(f"   MedQuad NIH                : ~8000 (NIH patient info)")
    print(f"   Synthetic Hindi/rural-India: {len(RURAL_INDIA_CASES + RURAL_INDIA_EN)*3} (high-priority conditions x3)")


if __name__ == "__main__":
    prepare_and_save()
