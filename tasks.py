"""
tasks.py
Contains all patient scenario datasets for Easy, Medium, and Hard tasks.
Each task is a list of PatientCase dicts — pre-built scenarios with known correct answers.
"""

# ─────────────────────────────────────────
# EASY TASK — 5 patients, no resource limits
# Agent just needs to assign correct priority
# ─────────────────────────────────────────
EASY_PATIENTS = [
    {
        "patient_id": "P001",
        "age": 58,
        "chief_complaint": "Chest pain radiating to left arm",
        "symptoms": ["chest pain", "sweating", "nausea", "shortness of breath"],
        "vitals": {"bp": "90/60", "hr": 112, "temp": 37.1, "spo2": 94},
        "arrival_step": 0,
        "current_severity": "critical",
        "correct_resource": "assign_icu",
    },
    {
        "patient_id": "P002",
        "age": 34,
        "chief_complaint": "High fever and confusion",
        "symptoms": ["fever", "confusion", "stiff neck"],
        "vitals": {"bp": "100/70", "hr": 105, "temp": 39.8, "spo2": 97},
        "arrival_step": 0,
        "current_severity": "serious",
        "correct_resource": "assign_doctor",
    },
    {
        "patient_id": "P003",
        "age": 22,
        "chief_complaint": "Twisted ankle while playing football",
        "symptoms": ["ankle pain", "mild swelling"],
        "vitals": {"bp": "120/80", "hr": 78, "temp": 36.6, "spo2": 99},
        "arrival_step": 0,
        "current_severity": "minor",
        "correct_resource": "defer",
    },
    {
        "patient_id": "P004",
        "age": 67,
        "chief_complaint": "Difficulty breathing",
        "symptoms": ["shortness of breath", "wheezing", "cyanosis"],
        "vitals": {"bp": "130/85", "hr": 98, "temp": 37.0, "spo2": 88},
        "arrival_step": 0,
        "current_severity": "critical",
        "correct_resource": "assign_ventilator",
    },
    {
        "patient_id": "P005",
        "age": 45,
        "chief_complaint": "Mild headache and dizziness",
        "symptoms": ["headache", "dizziness"],
        "vitals": {"bp": "135/88", "hr": 82, "temp": 37.2, "spo2": 98},
        "arrival_step": 0,
        "current_severity": "moderate",
        "correct_resource": "assign_doctor",
    },
]

# Correct answers for Easy grader (patient_id → correct_resource)
EASY_CORRECT_ANSWERS = {p["patient_id"]: p["correct_resource"] for p in EASY_PATIENTS}


# ─────────────────────────────────────────
# MEDIUM TASK — 10 patients, limited resources
# Resources: ICU beds=3, doctors=5, ventilators=2
# Agent must allocate optimally under constraints
# ─────────────────────────────────────────
MEDIUM_PATIENTS = [
    {
        "patient_id": "M001",
        "age": 72,
        "chief_complaint": "Stroke symptoms — face drooping",
        "symptoms": ["face drooping", "arm weakness", "speech difficulty"],
        "vitals": {"bp": "180/110", "hr": 88, "temp": 36.9, "spo2": 95},
        "arrival_step": 0,
        "current_severity": "critical",
        "correct_resource": "assign_icu",
    },
    {
        "patient_id": "M002",
        "age": 55,
        "chief_complaint": "Severe abdominal pain",
        "symptoms": ["abdominal pain", "vomiting", "rigid abdomen"],
        "vitals": {"bp": "95/65", "hr": 120, "temp": 38.5, "spo2": 96},
        "arrival_step": 0,
        "current_severity": "critical",
        "correct_resource": "assign_icu",
    },
    {
        "patient_id": "M003",
        "age": 40,
        "chief_complaint": "Breathing difficulty after allergic reaction",
        "symptoms": ["wheezing", "throat swelling", "hives"],
        "vitals": {"bp": "88/55", "hr": 130, "temp": 37.0, "spo2": 89},
        "arrival_step": 0,
        "current_severity": "critical",
        "correct_resource": "assign_ventilator",
    },
    {
        "patient_id": "M004",
        "age": 29,
        "chief_complaint": "Deep laceration on forearm",
        "symptoms": ["bleeding", "laceration", "pain"],
        "vitals": {"bp": "118/76", "hr": 90, "temp": 36.8, "spo2": 98},
        "arrival_step": 0,
        "current_severity": "serious",
        "correct_resource": "assign_doctor",
    },
    {
        "patient_id": "M005",
        "age": 63,
        "chief_complaint": "Uncontrolled diabetes — high blood sugar",
        "symptoms": ["excessive thirst", "frequent urination", "blurred vision"],
        "vitals": {"bp": "140/90", "hr": 85, "temp": 37.1, "spo2": 97},
        "arrival_step": 0,
        "current_severity": "serious",
        "correct_resource": "assign_doctor",
    },
    {
        "patient_id": "M006",
        "age": 18,
        "chief_complaint": "Panic attack",
        "symptoms": ["rapid breathing", "chest tightness", "trembling"],
        "vitals": {"bp": "125/82", "hr": 100, "temp": 36.7, "spo2": 99},
        "arrival_step": 0,
        "current_severity": "moderate",
        "correct_resource": "assign_doctor",
    },
    {
        "patient_id": "M007",
        "age": 50,
        "chief_complaint": "Broken wrist after fall",
        "symptoms": ["wrist pain", "swelling", "deformity"],
        "vitals": {"bp": "122/78", "hr": 76, "temp": 36.5, "spo2": 99},
        "arrival_step": 0,
        "current_severity": "moderate",
        "correct_resource": "assign_doctor",
    },
    {
        "patient_id": "M008",
        "age": 35,
        "chief_complaint": "Respiratory failure — known COPD",
        "symptoms": ["severe breathlessness", "cyanosis", "use of accessory muscles"],
        "vitals": {"bp": "110/70", "hr": 115, "temp": 37.3, "spo2": 82},
        "arrival_step": 0,
        "current_severity": "critical",
        "correct_resource": "assign_ventilator",
    },
    {
        "patient_id": "M009",
        "age": 25,
        "chief_complaint": "Mild fever and sore throat",
        "symptoms": ["fever", "sore throat", "runny nose"],
        "vitals": {"bp": "118/74", "hr": 80, "temp": 38.1, "spo2": 98},
        "arrival_step": 0,
        "current_severity": "minor",
        "correct_resource": "defer",
    },
    {
        "patient_id": "M010",
        "age": 80,
        "chief_complaint": "Hip fracture after fall",
        "symptoms": ["hip pain", "inability to walk", "swelling"],
        "vitals": {"bp": "138/88", "hr": 84, "temp": 36.9, "spo2": 97},
        "arrival_step": 0,
        "current_severity": "serious",
        "correct_resource": "assign_doctor",
    },
]

MEDIUM_CORRECT_ANSWERS = {p["patient_id"]: p["correct_resource"] for p in MEDIUM_PATIENTS}

# Resource limits for Medium task
MEDIUM_RESOURCES = {"icu_beds": 3, "doctors": 5, "ventilators": 2}


# ─────────────────────────────────────────
# HARD TASK — 15 patients, all resources constrained
# New patients arrive mid-episode, conditions deteriorate
# Resources: ICU beds=3, doctors=5, ventilators=2
# ─────────────────────────────────────────
HARD_INITIAL_PATIENTS = [
    {
        "patient_id": "H001",
        "age": 60,
        "chief_complaint": "Heart attack",
        "symptoms": ["chest pain", "sweating", "left arm pain"],
        "vitals": {"bp": "85/55", "hr": 118, "temp": 37.0, "spo2": 92},
        "arrival_step": 0,
        "current_severity": "critical",
        "correct_resource": "assign_icu",
    },
    {
        "patient_id": "H002",
        "age": 45,
        "chief_complaint": "Severe asthma attack",
        "symptoms": ["wheezing", "cyanosis", "cannot speak full sentences"],
        "vitals": {"bp": "108/72", "hr": 125, "temp": 37.1, "spo2": 85},
        "arrival_step": 0,
        "current_severity": "critical",
        "correct_resource": "assign_ventilator",
    },
    {
        "patient_id": "H003",
        "age": 70,
        "chief_complaint": "Altered consciousness",
        "symptoms": ["unconscious", "unresponsive", "pupils dilated"],
        "vitals": {"bp": "80/50", "hr": 55, "temp": 35.8, "spo2": 88},
        "arrival_step": 0,
        "current_severity": "critical",
        "correct_resource": "assign_icu",
    },
    {
        "patient_id": "H004",
        "age": 33,
        "chief_complaint": "Stab wound to abdomen",
        "symptoms": ["abdominal wound", "heavy bleeding", "pain"],
        "vitals": {"bp": "92/60", "hr": 122, "temp": 36.8, "spo2": 94},
        "arrival_step": 0,
        "current_severity": "critical",
        "correct_resource": "assign_icu",
    },
    {
        "patient_id": "H005",
        "age": 28,
        "chief_complaint": "Seizure — still ongoing",
        "symptoms": ["active seizure", "loss of consciousness", "muscle rigidity"],
        "vitals": {"bp": "145/95", "hr": 108, "temp": 37.5, "spo2": 91},
        "arrival_step": 0,
        "current_severity": "serious",
        "correct_resource": "assign_doctor",
    },
    {
        "patient_id": "H006",
        "age": 52,
        "chief_complaint": "Diabetic ketoacidosis",
        "symptoms": ["deep breathing", "fruity breath", "confusion"],
        "vitals": {"bp": "100/65", "hr": 110, "temp": 37.2, "spo2": 96},
        "arrival_step": 0,
        "current_severity": "serious",
        "correct_resource": "assign_doctor",
    },
    {
        "patient_id": "H007",
        "age": 19,
        "chief_complaint": "Drug overdose",
        "symptoms": ["pinpoint pupils", "slow breathing", "unresponsive"],
        "vitals": {"bp": "88/58", "hr": 50, "temp": 35.5, "spo2": 86},
        "arrival_step": 0,
        "current_severity": "critical",
        "correct_resource": "assign_ventilator",
    },
    {
        "patient_id": "H008",
        "age": 41,
        "chief_complaint": "Moderate burns on arms",
        "symptoms": ["burn wounds", "pain", "blistering"],
        "vitals": {"bp": "128/84", "hr": 95, "temp": 37.8, "spo2": 97},
        "arrival_step": 0,
        "current_severity": "serious",
        "correct_resource": "assign_doctor",
    },
]

# These patients arrive mid-episode (at step 3)
HARD_ARRIVING_PATIENTS = [
    {
        "patient_id": "H009",
        "age": 75,
        "chief_complaint": "Pulmonary embolism",
        "symptoms": ["sudden chest pain", "coughing blood", "rapid breathing"],
        "vitals": {"bp": "88/60", "hr": 128, "temp": 37.0, "spo2": 84},
        "arrival_step": 3,
        "current_severity": "critical",
        "correct_resource": "assign_icu",
    },
    {
        "patient_id": "H010",
        "age": 38,
        "chief_complaint": "Severe allergic reaction",
        "symptoms": ["facial swelling", "throat closing", "hives all over body"],
        "vitals": {"bp": "82/52", "hr": 135, "temp": 37.1, "spo2": 88},
        "arrival_step": 3,
        "current_severity": "critical",
        "correct_resource": "assign_ventilator",
    },
    {
        "patient_id": "H011",
        "age": 55,
        "chief_complaint": "Chest pain — possibly cardiac",
        "symptoms": ["chest tightness", "sweating", "jaw pain"],
        "vitals": {"bp": "95/65", "hr": 105, "temp": 37.0, "spo2": 93},
        "arrival_step": 3,
        "current_severity": "critical",
        "correct_resource": "assign_icu",
    },
    {
        "patient_id": "H012",
        "age": 30,
        "chief_complaint": "Broken leg after accident",
        "symptoms": ["leg pain", "deformity", "swelling"],
        "vitals": {"bp": "120/78", "hr": 88, "temp": 36.7, "spo2": 99},
        "arrival_step": 3,
        "current_severity": "moderate",
        "correct_resource": "assign_doctor",
    },
    {
        "patient_id": "H013",
        "age": 66,
        "chief_complaint": "Confusion and slurred speech",
        "symptoms": ["confusion", "slurred speech", "one-sided weakness"],
        "vitals": {"bp": "175/105", "hr": 92, "temp": 37.0, "spo2": 95},
        "arrival_step": 3,
        "current_severity": "serious",
        "correct_resource": "assign_doctor",
    },
    {
        "patient_id": "H014",
        "age": 23,
        "chief_complaint": "Mild sprain",
        "symptoms": ["ankle pain", "minor swelling"],
        "vitals": {"bp": "118/76", "hr": 72, "temp": 36.6, "spo2": 99},
        "arrival_step": 3,
        "current_severity": "minor",
        "correct_resource": "defer",
    },
    {
        "patient_id": "H015",
        "age": 48,
        "chief_complaint": "Respiratory distress worsening",
        "symptoms": ["severe breathlessness", "accessory muscle use", "cyanosis"],
        "vitals": {"bp": "105/68", "hr": 118, "temp": 37.2, "spo2": 83},
        "arrival_step": 3,
        "current_severity": "critical",
        "correct_resource": "assign_ventilator",
    },
]

HARD_CORRECT_ANSWERS = {
    p["patient_id"]: p["correct_resource"]
    for p in HARD_INITIAL_PATIENTS + HARD_ARRIVING_PATIENTS
}

# Resource limits for Hard task (same as Medium — but more patients competing)
HARD_RESOURCES = {"icu_beds": 3, "doctors": 5, "ventilators": 2}

# Severity weights for Hard grader (critical patients worth more)
SEVERITY_WEIGHTS = {
    "critical": 3.0,
    "serious": 2.0,
    "moderate": 1.0,
    "minor": 0.5,
}