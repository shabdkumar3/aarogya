"""
Aarogya Extensive Dataset Preparation
======================================
Sources:
  1. lavita/ChatDoctor-HealthCareMagic-100k  (100K real doctor Q&A)
  2. medalpaca/medical_meadow_healthcaremagic (226K clinical exchanges)
  3. medalpaca/medical_meadow_mediqa          (2K expert QA)
  4. keivalya/MedQuad-MedicalQnADataset       (47K NIH QA)
  5. Synthetic Hindi/rural-India triage       (25 handcrafted x3)

Target: ~15K train + 2K val
"""
import hashlib, json, random, re, sys

SYSTEM_PROMPT = (
    "You are Aarogya, a medical triage assistant for ASHA community health workers in rural India.\n"
    "Given a symptom description, output ONLY a valid JSON triage assessment.\n\n"
    "Required JSON format:\n"
    '{"conditions":["most likely","differential"],"urgency":"Monitor at Home",'
    '"next_steps":["step1","step2","step3"],"red_flags":["sign1","sign2"],'
    '"asha_note":"One clear action sentence for the ASHA worker."}\n\n'
    'urgency must be EXACTLY: "Monitor at Home", "Visit PHC", or "Emergency Referral"\n'
    "Respond ONLY with the JSON object. No explanation, no preamble."
)

def make_entry(question, answer_text):
    """Build a single training sample."""
    q = re.sub(r'\s+', ' ', str(question or '')).strip()
    a = re.sub(r'\s+', ' ', str(answer_text or '')).strip()
    if len(q) < 15 or len(a) < 20:
        return None
    structured = _make_json(q, a)
    text = (
        f"<start_of_turn>user\n{SYSTEM_PROMPT}\n\nSymptoms: {q}<end_of_turn>\n"
        f"<start_of_turn>model\n{structured}<end_of_turn>"
    )
    # Dedup key = MD5 of the question (not the template prefix!)
    key = hashlib.md5(q.lower().encode()).hexdigest()
    return {"text": text, "_key": key}

EMERGENCY_KW = ["emergency","immediately","severe","critical","hospital","icu",
                "urgent","life-threatening","unconscious","seizure","poisoning"]
PHC_KW       = ["consult","doctor","physician","clinic","test","blood","scan",
                "examination","prescription","specialist","x-ray","lab"]

def _classify(text):
    t = text.lower()
    if any(k in t for k in EMERGENCY_KW): return "Emergency Referral"
    if any(k in t for k in PHC_KW):       return "Visit PHC"
    return "Monitor at Home"

def _make_json(q, a):
    urgency = _classify(a)
    cond    = re.sub(r'^(what|how|why|can|is|are|does|do|should)\s+', '', q.lower(), flags=re.I)
    cond    = re.sub(r'\?.*', '', cond).strip()[:60].title() or "Unspecified Condition"
    steps = {"Emergency Referral": ["Call emergency transport immediately",
                                     "Do not leave patient alone",
                                     "Rush to nearest hospital"],
             "Visit PHC":          ["Visit Primary Health Centre within 24 hours",
                                     "Monitor vitals and symptom progression",
                                     "Bring previous prescriptions if any"],
             "Monitor at Home":    ["Ensure rest and adequate oral fluids (ORS if needed)",
                                     "Monitor temperature every 4 hours",
                                     "Return if no improvement in 48 hours"]}
    flags = {"Emergency Referral": ["Loss of consciousness or seizures",
                                     "Difficulty breathing"],
             "Visit PHC":           ["Fever above 103F for more than 2 days",
                                     "Symptoms worsening despite home care"],
             "Monitor at Home":     ["Sudden worsening of symptoms",
                                     "New symptoms appear (rash, bleeding, fits)"]}
    obj = {"conditions": [cond], "urgency": urgency,
           "next_steps": steps[urgency], "red_flags": flags[urgency],
           "asha_note": f"Follow up in 48 hours. Urgency: {urgency}."}
    return json.dumps(obj, ensure_ascii=False)

# ── Source loaders ──────────────────────────────────────────────────────────

def _load_hf(dataset_id, split, question_field, answer_field, n, required=False):
    print(f"  Loading {dataset_id} (up to {n} rows)...")
    try:
        from datasets import load_dataset
        ds = load_dataset(dataset_id, split=split, trust_remote_code=True)
        out = []
        for item in ds.select(range(min(n, len(ds)))):
            e = make_entry(item.get(question_field, ""), item.get(answer_field, ""))
            if e:
                out.append(e)
        print(f"    → {len(out)} valid samples")
        return out
    except Exception as ex:
        msg = f"    ⚠️  SKIPPED {dataset_id}: {ex}"
        print(msg)
        if required:
            raise RuntimeError(msg)
        return []

def load_all_sources():
    all_data = []

    print("\n[1/5] ChatDoctor-HealthCareMagic-100k")
    all_data += _load_hf("lavita/ChatDoctor-HealthCareMagic-100k",
                          "train", "input", "output", 25000, required=False)

    print("\n[2/5] Medalpaca medical_meadow_healthcaremagic")
    all_data += _load_hf("medalpaca/medical_meadow_healthcaremagic",
                          "train", "input", "output", 15000)

    print("\n[3/5] Medalpaca medical_meadow_mediqa")
    all_data += _load_hf("medalpaca/medical_meadow_mediqa",
                          "train", "input", "output", 5000)

    print("\n[4/5] MedQuad-MedicalQnADataset")
    all_data += _load_hf("keivalya/MedQuad-MedicalQnADataset",
                          "train", "Question", "Answer", 10000)

    print("\n[5/5] Synthetic Hindi/rural-India cases")
    all_data += _load_synthetic()

    return all_data

# ── Synthetic rural-India examples ──────────────────────────────────────────

_SYNTHETIC = [
    ("Bachche ko 3 din se thand ke saath tez bukhar, kaanp raha hai, pond ke paas rehta hai",
     '{"conditions":["Malaria","Dengue"],"urgency":"Visit PHC","next_steps":["RDT test at PHC today","Keep hydrated with ORS","No aspirin for children"],"red_flags":["Fits or unconsciousness","Fever above 104F"],"asha_note":"Alternate-day fever near water = malaria risk, PHC today."}'),
    ("2 mahine se khansi, balgam mein khoon, wazn ghata hai, raat ko paseena",
     '{"conditions":["Pulmonary Tuberculosis"],"urgency":"Visit PHC","next_steps":["Sputum AFB test at PHC","Start DOTS if confirmed","Isolate and ventilate room"],"red_flags":["Massive hemoptysis","Breathlessness at rest"],"asha_note":"2-month cough + blood = TB suspected. Refer for sputum test today."}'),
    ("1 saal ke bachche ko kal se dast 8-10 baar, aankhein andar dhans gayi",
     '{"conditions":["Severe Dehydration","Acute Gastroenteritis"],"urgency":"Emergency Referral","next_steps":["ORS immediately tiny sips","Rush to hospital for IV fluids","Do not give anti-diarrheal drugs"],"red_flags":["Sunken eyes = severe dehydration","No urination in 6 hours"],"asha_note":"Sunken eyes in infant = Emergency. Give ORS while rushing to hospital NOW."}'),
    ("8 mahine pregnant, haath-paon sujan, sar dard, aankhon ke aage andhera",
     '{"conditions":["Pre-eclampsia","Eclampsia Risk"],"urgency":"Emergency Referral","next_steps":["Rush to FRU immediately","Left lateral position in transport","No BP medication without doctor"],"red_flags":["Seizures = eclampsia","BP above 160/110"],"asha_note":"Swelling + headache + vision in 8-month pregnancy = pre-eclampsia EMERGENCY. Transport now."}'),
    ("Saanp ne kaata, jagah sunn, pair mein sujan aa rahi hai, ulti",
     '{"conditions":["Venomous Snakebite","Envenomation"],"urgency":"Emergency Referral","next_steps":["Immobilize bitten limb below heart","Rush to hospital for ASV","No cut-suck or tourniquet"],"red_flags":["Drooping eyelids = neurotoxic","Bleeding from bite or gums"],"asha_note":"Snakebite with swelling = Emergency. Immobilize and rush to hospital NOW for ASV."}'),
    ("Bachche ko tez bukhar, sharir par laal daane, haath-paon mein dard",
     '{"conditions":["Dengue Fever","Chikungunya"],"urgency":"Visit PHC","next_steps":["NS1 antigen test at PHC","Paracetamol only - NO aspirin","ORS and coconut water"],"red_flags":["Bleeding gums or nose","Platelet below 50000"],"asha_note":"Fever with rash = dengue possible. Test today. Avoid ibuprofen/aspirin."}'),
    ("2 saal ka bachcha bahut patla, haath-paon sujan, bal jhad rahe",
     '{"conditions":["Severe Acute Malnutrition","Kwashiorkor"],"urgency":"Visit PHC","next_steps":["Enroll in NRC today","Start RUTF if available","Screen for infections"],"red_flags":["Breathing difficulty","Persistent diarrhea"],"asha_note":"Wasting + edema = SAM. NRC admission today, notify Anganwadi worker."}'),
    ("Pregnant woman pale, breathless walking, eating mud/chalk",
     '{"conditions":["Severe Iron-Deficiency Anemia","Pica in Pregnancy"],"urgency":"Visit PHC","next_steps":["Hemoglobin test at PHC","Start IFA tablets immediately","Iron-rich foods: jaggery, greens"],"red_flags":["Hb below 7 g/dL","Chest pain or fainting"],"asha_note":"Pica + pallor in pregnancy = severe anemia. Hb test today and IFA now."}'),
    ("Kutte ne kaata, khoon aa raha, jaanwar pagal lag raha tha",
     '{"conditions":["Animal Bite","Rabies Risk"],"urgency":"Emergency Referral","next_steps":["Wash wound soap + water 15 minutes","ARV vaccine at PHC today - first dose within 24h","Report to health department"],"red_flags":["Bite on face/neck = HIGH RISK","Multiple bites"],"asha_note":"Dog bite = start ARV today. Wash with soap NOW, PHC within hours."}'),
    ("Worker collapsed in field, not sweating, skin hot dry, confused",
     '{"conditions":["Heat Stroke","Heat Exhaustion"],"urgency":"Emergency Referral","next_steps":["Move to shade, cool with wet cloth","Fan continuously","Rush to hospital"],"red_flags":["Unconscious or seizures","No improvement with cooling in 15 min"],"asha_note":"Hot dry skin + confusion = heat stroke EMERGENCY. Cool and transport immediately."}'),
    ("Gaon mein kai logon ko ek saath dast aur ulti, paani jaisa",
     '{"conditions":["Cholera Outbreak","Acute Watery Diarrhea"],"urgency":"Emergency Referral","next_steps":["ORS for all affected immediately","Report to Block Medical Officer NOW","Boil all drinking water"],"red_flags":["Rice-water stools = severe cholera","Multiple cases = epidemic risk"],"asha_note":"Cluster diarrhea = notifiable disease. Report to BMO TODAY."}'),
    ("Navjaat shishu 2 din ka, peela pad raha, doodh nahi pi raha",
     '{"conditions":["Neonatal Jaundice","Neonatal Sepsis Risk"],"urgency":"Emergency Referral","next_steps":["Rush to SNCU for bilirubin test","No home remedies","Monitor feeding and lethargy"],"red_flags":["Jaundice in first 24 hours","Not feeding at all"],"asha_note":"2-day-old with jaundice not feeding = SNCU emergency NOW."}'),
    ("55 saal, sar bahut dard, chakkar, BP 180/110",
     '{"conditions":["Hypertensive Crisis","Uncontrolled Hypertension"],"urgency":"Emergency Referral","next_steps":["Rush to PHC/hospital immediately","Lay patient flat, no exertion","No extra BP tablet without doctor"],"red_flags":["Chest pain or breathlessness","Slurred speech or vision loss"],"asha_note":"BP 180/110 with symptoms = hypertensive crisis. Hospital NOW."}'),
    ("5 saal ka bachcha, 2 din se sardi-khansi, halka bukhar, khel raha",
     '{"conditions":["Upper Respiratory Tract Infection","Common Cold"],"urgency":"Monitor at Home","next_steps":["Paracetamol syrup for fever","Saline nasal drops","Warm fluids - soup, ginger tea"],"red_flags":["Breathing fast or difficult","Fever above 103F for 3+ days"],"asha_note":"Mild cold in active child. Home care 3 days, return if breathing changes."}'),
    ("Haath mein sunn jagah, skin par safed dabbe, kaafi samay se",
     '{"conditions":["Leprosy (Hansen disease)","Vitiligo"],"urgency":"Visit PHC","next_steps":["Skin slit smear test at PHC","Start MDT if confirmed","Counsel: leprosy is curable"],"red_flags":["Claw hand or foot drop","Multiple patches spreading"],"asha_note":"Painless pale patch + numbness = leprosy. PHC for MDT today - confidential and curable."}'),
    ("Child 3 years, MUAC 10.5cm, very weak, bilateral pitting edema",
     '{"conditions":["Severe Acute Malnutrition","SAM with Complications"],"urgency":"Emergency Referral","next_steps":["MUAC below 11.5cm = NRC admission required","Screen for malaria TB pneumonia","Start F-75 therapeutic milk at NRC"],"red_flags":["MUAC below 11.5cm","Medical complications present"],"asha_note":"MUAC 10.5cm = SAM. NRC admission today - high mortality risk."}'),
    ("Patient high fever 102F for 3 days, severe headache, stiff neck, vomiting",
     '{"conditions":["Bacterial Meningitis","Viral Encephalitis"],"urgency":"Emergency Referral","next_steps":["Rush to hospital IMMEDIATELY","Do not wait - meningitis is fatal if delayed","Keep patient still and calm"],"red_flags":["Stiff neck + fever = meningitis until proven otherwise","Rash (purpura) = meningococcal = CRITICAL"],"asha_note":"Fever + stiff neck = meningitis emergency. Hospital in next 30 minutes."}'),
    ("Lady 40 years, painless hard lump in breast 2 months, nipple discharge",
     '{"conditions":["Breast Malignancy Suspected","Breast Abscess"],"urgency":"Visit PHC","next_steps":["Urgent FNAC/biopsy at District Hospital","No massage or home remedies","Register under NCD screening"],"red_flags":["Skin dimpling (peau d orange)","Axillary lymph node enlargement"],"asha_note":"Hard painless breast lump = urgent biopsy. Same-week District Hospital appointment."}'),
    ("Pregnant woman 7 months, baby movements reduced for 2 days",
     '{"conditions":["Reduced Fetal Movement","Fetal Distress"],"urgency":"Visit PHC","next_steps":["Count kicks - less than 10 in 2 hours = concern","PHC same day for fetal heart monitoring","Do not reassure without monitoring"],"red_flags":["No movement 12+ hours","Vaginal bleeding or severe pain"],"asha_note":"Reduced baby movement at 7 months = same-day PHC check required."}'),
    ("6-month-old baby with 10 watery stools, sunken eyes, not crying, cold hands",
     '{"conditions":["Severe Dehydration","Acute Gastroenteritis"],"urgency":"Emergency Referral","next_steps":["ORS tiny sips while rushing to hospital","IV fluids needed urgently","Keep baby warm during transport"],"red_flags":["No tears when crying","Limp and unresponsive"],"asha_note":"Severe dehydration in infant - IV fluids needed NOW. Rush to hospital."}'),
    ("Farmer snakebite field 30 min ago, leg swelling rapidly, nausea vomiting",
     '{"conditions":["Viper Envenomation","Snakebite"],"urgency":"Emergency Referral","next_steps":["Immobilize leg at heart level","Hospital with ASV immediately","Remove tight clothing near bite"],"red_flags":["Gum bleeding = coagulopathy","Drooping eyelids = neurotoxic"],"asha_note":"Snakebite + rapid swelling = viperine envenomation. Hospital NOW for ASV."}'),
    ("Aankhein laal hain, cheech aa rahi hai, subah aankhein band ho jaati",
     '{"conditions":["Acute Conjunctivitis","Bacterial Eye Infection"],"urgency":"Monitor at Home","next_steps":["Clean eye with boiled water 4x daily","Antibiotic drops from PHC if available","Do not share towel - very contagious"],"red_flags":["Loss of vision","Severe eye pain"],"asha_note":"Conjunctivitis - isolate to prevent spread, PHC for drops if not improving in 3 days."}'),
    ("Adult watery diarrhea 5 times, mild stomach cramps, thirsty",
     '{"conditions":["Gastroenteritis","Food Poisoning"],"urgency":"Monitor at Home","next_steps":["ORS after every loose stool 250ml","Avoid spicy oily food 48 hours","Handwash with soap after toilet"],"red_flags":["10+ stools per day","Blood in stool"],"asha_note":"Mild case - ORS at home, monitor 48 hours and follow up."}'),
    ("TB patient on DOTS for 2 months, stopped taking medicine last week",
     '{"conditions":["TB Treatment Non-Adherence","Drug Resistance Risk"],"urgency":"Visit PHC","next_steps":["Restart DOTS immediately - go to PHC today","Counsel on drug resistance risk","ASHA worker to supervise doses daily"],"red_flags":["Resuming after more than 2 weeks = restart full course","Worsening symptoms"],"asha_note":"TB non-adherence = drug resistance risk. Restart DOTS at PHC TODAY - this is critical."}'),
    ("Newborn 3 days, not feeding, temperature low, floppy",
     '{"conditions":["Neonatal Sepsis","Hypothermia"],"urgency":"Emergency Referral","next_steps":["Kangaroo care for warmth immediately","Rush to SNCU","Do not wait - neonatal sepsis progresses in hours"],"red_flags":["Floppy/limp baby","Temperature below 36C"],"asha_note":"Floppy newborn not feeding = neonatal emergency. SNCU NOW - every minute counts."}'),
]

def _load_synthetic():
    out = []
    for q, a in _SYNTHETIC:
        e = make_entry(q, a)
        if e:
            # Override the pre-built JSON answer directly (skip _make_json)
            e["text"] = (
                f"<start_of_turn>user\n{SYSTEM_PROMPT}\n\nSymptoms: {q}<end_of_turn>\n"
                f"<start_of_turn>model\n{a}<end_of_turn>"
            )
            out.append(e)
    # 4x augmentation (more weight for rural-India cases)
    out = out * 4
    # Re-assign unique keys after multiplication
    for i, item in enumerate(out):
        item["_key"] = hashlib.md5(f"{item['text']}_{i}".encode()).hexdigest()
    random.shuffle(out)
    print(f"    → {len(out)} synthetic samples (25 cases × 4 augmented)")
    return out

# ── Main ────────────────────────────────────────────────────────────────────

def prepare_and_save(train_size=15000, val_size=2000):
    all_data = load_all_sources()

    print(f"\nTotal raw samples: {len(all_data)}")

    if len(all_data) == 0:
        raise RuntimeError(
            "No data collected! All sources failed.\n"
            "Check internet connection and that Kaggle has Internet ON."
        )

    # Deduplicate by question MD5 key
    seen  = set()
    deduped = []
    for item in all_data:
        k = item.get("_key", hashlib.md5(item["text"].encode()).hexdigest())
        if k not in seen:
            seen.add(k)
            deduped.append(item)

    print(f"After deduplication: {len(deduped)} unique samples")

    if len(deduped) < 50:
        raise RuntimeError(
            f"Only {len(deduped)} samples after dedup — dataset sources likely failed.\n"
            "Check that internet is ON in Kaggle and rerun Cell 3."
        )

    random.seed(42)
    random.shuffle(deduped)

    # Safe split — handle case where total < val_size
    total = len(deduped)
    actual_val   = min(val_size, max(1, total // 5))       # at most 20% for val
    actual_train = min(train_size, total - actual_val)

    if actual_train <= 0:
        raise RuntimeError(f"Not enough data: {total} samples, need at least {actual_val + 1}.")

    train = deduped[:actual_train]
    val   = deduped[actual_train:actual_train + actual_val]

    with open("train_data.jsonl", "w", encoding="utf-8") as f:
        for item in train:
            row = {"text": item["text"]}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    with open("val_data.jsonl", "w", encoding="utf-8") as f:
        for item in val:
            row = {"text": item["text"]}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"\n✅ Dataset ready!")
    print(f"   Train : {len(train):,} samples → train_data.jsonl")
    print(f"   Val   : {len(val):,} samples   → val_data.jsonl")
    print(f"\nSource breakdown:")
    print(f"   ChatDoctor-HealthCareMagic : up to 25000")
    print(f"   Medalpaca HealthCareMagic  : up to 15000")
    print(f"   Medalpaca MediQA           : up to 5000")
    print(f"   MedQuad NIH                : up to 10000")
    print(f"   Synthetic Hindi/rural-India: {len(_SYNTHETIC) * 4} (25 cases × 4)")


if __name__ == "__main__":
    prepare_and_save()
