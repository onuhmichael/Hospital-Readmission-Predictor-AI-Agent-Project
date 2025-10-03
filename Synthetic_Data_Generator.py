"""
Synthetic_Data_Generator_Appender.py

Continuously generates synthetic patient records and appends them to CSV and NDJSON files.

Default behavior:
- Appends 100 records per insertion (changeable via --n-per-interval or the DEFAULT_N_PER_INTERVAL constant).
- Inserts every 2 seconds (changeable via --interval or the DEFAULT_INTERVAL_SECONDS constant).
- Writes to: C:\Hospital Readmission Predictor AI Agent Project\HRPA_Data\<out-prefix>.csv
             C:\Hospital Readmission Predictor AI Agent Project\HRPA_Data\<out-prefix>.ndjson

How to run (Windows):
    python "C:\Hospital Readmission Predictor AI Agent Project\Synthetic_Data_Generator_Appender.py"

How to change common settings:
- To change batch size at runtime: add --n-per-interval 1000
- To change interval at runtime: add --interval 1.5
- To change file prefix at runtime: add --out-prefix mydata
- To change defaults inside the file: edit DEFAULT_* constants below

Stop the script with Ctrl+C. The script writes full batches atomically (per batch), prints a progress line each insertion, and exits cleanly on interrupt.
"""

import argparse
import csv
import json
import os
import random
import sys
import time
import uuid
from datetime import datetime, timedelta

# Optional modules improve distribution realism; script falls back to stdlib if unavailable.
try:
    import numpy as np
    from faker import Faker
except Exception:
    np = None
    from faker import Faker

fake = Faker()

# ------------- USER-CONFIGURABLE DEFAULTS -------------
# Change these constants directly if you want new defaults baked into the script.
DEFAULT_N_PER_INTERVAL = 100     # Default rows appended per insertion (user requested 100)
DEFAULT_INTERVAL_SECONDS = 2.0   # Default seconds between insertions
# Data directory to store outputs. Change to any valid Windows path as required.
DATA_DIR = r"C:\Hospital Readmission Predictor AI Agent Project\HRPA_Data"
# Default output file prefix (CSV and NDJSON will share this prefix)
DEFAULT_OUT_PREFIX = "patients"
# ------------- END USER-CONFIGURABLE DEFAULTS -------------

# Ensure data directory exists before writing
os.makedirs(DATA_DIR, exist_ok=True)

# CSV column order (change order or add/remove fields here and propagate to record builder below)
COLUMNS = [
    "PatientID", "Age", "Gender", "AdmissionDate", "DischargeDate", "Diagnosis", "LengthOfStay",
    "PriorAdmissions", "Medications", "ReadmittedWithin30Days", "BMI", "SmokingStatus",
    "AlcoholUse", "BloodPressure", "CholesterolLevel", "HbA1c", "FollowUpAppointmentScheduled",
    "InsuranceType", "RecordGeneratedAt"
]

# ------------- Data pools and parameter tables -------------
# Modify diagnoses, meds, and insurance distributions here to reflect your population.
DIAGNOSES = {
    "Hypertension": {"base_los": 3, "los_sd": 2, "readmit_base": 0.05},
    "Heart Failure": {"base_los": 6, "los_sd": 4, "readmit_base": 0.18},
    "Pneumonia": {"base_los": 5, "los_sd": 3, "readmit_base": 0.12},
    "Stroke": {"base_los": 8, "los_sd": 5, "readmit_base": 0.20},
    "Diabetes": {"base_los": 4, "los_sd": 3, "readmit_base": 0.10},
    "COPD": {"base_los": 5, "los_sd": 3, "readmit_base": 0.15},
    "Fracture": {"base_los": 2, "los_sd": 1, "readmit_base": 0.04},
    "Sepsis": {"base_los": 10, "los_sd": 7, "readmit_base": 0.22},
    "Cancer": {"base_los": 7, "los_sd": 6, "readmit_base": 0.14},
    "Other": {"base_los": 3, "los_sd": 2, "readmit_base": 0.06},
}

GENDERS = ["Male", "Female", "Other"]
SMOKING_STATUSES = ["Never", "Former", "Current"]
ALCOHOL_USE = ["None", "Moderate", "Heavy"]
INSURANCE_TYPES = ["Private", "Public", "Self-Pay"]

MEDICATION_POOLS = {
    "Hypertension": ["ACE Inhibitors", "Beta Blockers", "Calcium Channel Blockers", "Diuretics"],
    "Heart Failure": ["ACE Inhibitors", "Beta Blockers", "Diuretics", "Aldosterone Antagonists"],
    "Pneumonia": ["Antibiotics", "Bronchodilators"],
    "Stroke": ["Antiplatelets", "Anticoagulants", "Statins"],
    "Diabetes": ["Insulin", "Metformin", "SGLT2 Inhibitors"],
    "COPD": ["Bronchodilators", "Inhaled Steroids"],
    "Fracture": ["Analgesics", "Opioids"],
    "Sepsis": ["Antibiotics", "Vasopressors"],
    "Cancer": ["Chemotherapy", "Analgesics"],
    "Other": ["Analgesics", "Multivitamins"],
}
# ------------- End data pools -------------

# ---------------- Realistic random helper functions ----------------
# These functions implement correlated randomness; change weights and distributions here.

def realistic_age():
    """Return an age sampled from a mixed distribution to mimic inpatient populations.
    Edit the cluster probabilities or parameters to shift population age profile."""
    if random.random() < 0.65:
        # Older cluster (most inpatients)
        if np:
            return int(max(18, min(100, int(np.random.normal(75, 8)))))
        return random.randint(65, 95)
    else:
        # Younger/middle-aged cluster
        if np:
            return int(max(18, min(64, int(np.random.normal(45, 12)))))
        return random.randint(18, 64)

def realistic_bmi(age):
    """BMI with mild age dependence. Tweak means and sds for different BMI profiles."""
    if np:
        if age < 30:
            return round(float(np.clip(np.random.normal(24, 3.5), 15, 40)), 1)
        if age < 60:
            return round(float(np.clip(np.random.normal(28, 4.5), 18, 45)), 1)
        return round(float(np.clip(np.random.normal(27, 4.0), 18, 42)), 1)
    else:
        base = 24 if age < 30 else (28 if age < 60 else 27)
        return round(min(max(random.gauss(base, 4), 15), 45), 1)

def realistic_bp(age, diagnosis):
    """Systolic/diastolic BP formatted as 'S/D'. Adjust shifts for specific diagnoses here."""
    sys = int(random.gauss(125, 12))
    dia = int(random.gauss(78, 8))
    if diagnosis == "Hypertension" or age > 70:
        sys += abs(int(random.gauss(10, 8)))
    if diagnosis in ("Sepsis", "Heart Failure") and random.random() < 0.3:
        sys = max(80, sys - int(random.gauss(30, 10)))
        dia = max(40, dia - int(random.gauss(15, 6)))
    if np:
        sys = int(np.clip(sys, 70, 220)); dia = int(np.clip(dia, 40, 130))
    else:
        sys = max(70, min(sys, 220)); dia = max(40, min(dia, 130))
    return f"{sys}/{dia}"

def realistic_cholesterol(age):
    """Total cholesterol mg/dL with small age effect."""
    base = 190 + (0.1 * max(age - 40, 0))
    val = int(random.gauss(base, 35))
    return int(max(100, min(val, 400)))

def realistic_hba1c(diagnosis):
    """HbA1c higher for diabetes patients; adjust means/sds as needed."""
    if diagnosis == "Diabetes":
        return round(max(5.6, min(random.gauss(8.5, 1.9), 15)), 1)
    return round(max(4.5, min(random.gauss(5.4, 0.4), 7.5)), 1)

def select_medications(diagnosis):
    """Select 1-3 meds from the diagnosis-specific pool. Modify pool for new drugs."""
    pool = MEDICATION_POOLS.get(diagnosis, MEDICATION_POOLS["Other"])
    k = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
    meds = random.sample(pool, min(k, len(pool)))
    return "; ".join(meds)

def length_of_stay_for(diagnosis, age):
    """Generate LengthOfStay with a skew and rare long tails. Adjust tail probability as needed."""
    params = DIAGNOSES.get(diagnosis, DIAGNOSES["Other"])
    base = params["base_los"]
    if np:
        los = int(max(1, round(np.random.lognormal(mean=np.log(max(0.9, base)), sigma=0.5))))
    else:
        los = max(1, int(random.gauss(base, params["los_sd"])))
    if age >= 80:
        los += int(random.choice([0, 1, 2]))
    if random.random() < 0.02:
        los += random.randint(5, 30)
    return los

def prior_admissions_for(age):
    """Prior admissions correlated with age. Adjust lambda values to tune counts."""
    lam = 0.2 if age < 40 else (0.7 if age < 65 else 1.6)
    if np:
        val = int(np.random.poisson(lam))
    else:
        val = sum(1 for _ in range(6) if random.random() < lam/1.5)
    return int(min(val, 20))

def smoking_for(age):
    """Smoking status probabilities by age group. Change weights to reflect target population."""
    if age < 30:
        return random.choices(SMOKING_STATUSES, weights=[0.6, 0.15, 0.25])[0]
    if age < 65:
        return random.choices(SMOKING_STATUSES, weights=[0.5, 0.25, 0.25])[0]
    return random.choices(SMOKING_STATUSES, weights=[0.6, 0.3, 0.1])[0]

def alcohol_for(_age):
    """Alcohol use probabilities. Edit weights for different communities."""
    return random.choices(ALCOHOL_USE, weights=[0.35, 0.55, 0.10])[0]

def readmission_risk(age, diagnosis, prior_adm, los, smoking, bmi):
    """Additive risk model for readmission probability. Tweak coefficients for calibration."""
    base = DIAGNOSES.get(diagnosis, DIAGNOSES["Other"])["readmit_base"]
    p = base
    p += 0.01 * max(0, (age - 50) / 10)
    p += 0.03 * min(prior_adm, 5)
    p += 0.02 * max(0, (bmi - 25) / 5)
    p += 0.02 if smoking == "Current" else 0.0
    p += 0.01 if los > 7 else 0.0
    return min(max(p, 0.01), 0.9)
# ------------- End helper functions -------------

# ---------------- Record assembly ----------------
def admission_and_discharge_dates(length_of_stay_days):
    """Create admission and discharge dates in YYYY-MM-DD; adjust lookback window here."""
    days_back = int(abs(random.gauss(200, 150)))  # admissions within ~2 years, skewed recent
    admission = datetime.now() - timedelta(days=days_back) + timedelta(minutes=random.randint(0, 1440))
    discharge = admission + timedelta(days=length_of_stay_days, hours=random.randint(0, 23), minutes=random.randint(0, 59))
    return admission.strftime("%Y-%m-%d"), discharge.strftime("%Y-%m-%d")

def generate_patient_record():
    """Build one coherent patient record dict. Edit fields here to change output schema."""
    age = realistic_age()
    gender = random.choice(GENDERS)

    # Age-aware diagnosis sampling. Edit these weight vectors to change diagnosis mix by age band.
    if age >= 80:
        diag_weights = [0.15, 0.20, 0.05, 0.05, 0.08, 0.12, 0.05, 0.05, 0.10, 0.15]
    elif age >= 65:
        diag_weights = [0.20, 0.18, 0.06, 0.07, 0.08, 0.10, 0.04, 0.05, 0.07, 0.15]
    else:
        diag_weights = [0.18, 0.08, 0.06, 0.03, 0.12, 0.05, 0.12, 0.04, 0.15, 0.17]
    diagnosis = random.choices(list(DIAGNOSES.keys()), weights=diag_weights, k=1)[0]

    los = length_of_stay_for(diagnosis, age)
    prior_adm = prior_admissions_for(age)
    adm_date, dis_date = admission_and_discharge_dates(los)

    bmi = realistic_bmi(age)
    smoking = smoking_for(age)
    alcohol = alcohol_for(age)
    bp = realistic_bp(age, diagnosis)
    chol = realistic_cholesterol(age)
    hba1c = realistic_hba1c(diagnosis)
    meds = select_medications(diagnosis)
    follow_up = 1 if random.random() < 0.7 else 0
    insurance = random.choices(INSURANCE_TYPES, weights=[0.5, 0.4, 0.1])[0]

    readmit_prob = readmission_risk(age, diagnosis, prior_adm, los, smoking, bmi)
    readmitted = 1 if random.random() < readmit_prob else 0

    # PatientID: 8 hex characters for compactness; swap to uuid.uuid4().hex for full UUID
    patient_id = uuid.uuid4().hex[:8]

    return {
        "PatientID": patient_id,
        "Age": int(age),
        "Gender": gender,
        "AdmissionDate": adm_date,
        "DischargeDate": dis_date,
        "Diagnosis": diagnosis,
        "LengthOfStay": int(los),
        "PriorAdmissions": int(prior_adm),
        "Medications": meds,
        "ReadmittedWithin30Days": int(readmitted),
        "BMI": float(bmi),
        "SmokingStatus": smoking,
        "AlcoholUse": alcohol,
        "BloodPressure": bp,
        "CholesterolLevel": int(chol),
        "HbA1c": float(hba1c),
        "FollowUpAppointmentScheduled": int(follow_up),
        "InsuranceType": insurance,
        "RecordGeneratedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

# ---------------- I/O helpers that append ----------------
def append_to_csv(rows, csv_path):
    """Append rows to CSV. Writes header only if file is missing or empty."""
    write_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if write_header:
            writer.writeheader()
        for r in rows:
            writer.writerow(r)

def append_to_ndjson(rows, json_path):
    """Append rows to NDJSON (one JSON object per line). Safe for streaming appends."""
    with open(json_path, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, default=str) + "\n")

# ---------------- Main loop ----------------
def run_loop(n_per_interval, interval_seconds, out_prefix):
    csv_path = os.path.join(DATA_DIR, f"{out_prefix}.csv")
    json_path = os.path.join(DATA_DIR, f"{out_prefix}.ndjson")

    total_written = 0
    start_time = time.time()
    print(f"Appending to:\n  CSV:  {csv_path}\n  NDJSON: {json_path}\nBatch size: {n_per_interval} every {interval_seconds} seconds\nPress Ctrl+C to stop.")
    try:
        while True:
            batch = [generate_patient_record() for _ in range(n_per_interval)]
            append_to_csv(batch, csv_path)
            append_to_ndjson(batch, json_path)
            total_written += len(batch)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Appended {len(batch)} record(s) (total {total_written}).")
            # Sleep in short slices to allow quick KeyboardInterrupt handling
            slept = 0.0
            while slept < interval_seconds:
                time.sleep(min(0.5, interval_seconds - slept))
                slept += min(0.5, interval_seconds - slept)
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\nInterrupted by user. Wrote {total_written} record(s) in {elapsed:.1f} seconds.")
        sys.exit(0)

# ---------------- Command-line interface ----------------
def main():
    parser = argparse.ArgumentParser(description="Continuously append synthetic patient records to CSV and NDJSON.")
    parser.add_argument("--n-per-interval", type=int, default=DEFAULT_N_PER_INTERVAL, help="Number of records appended each interval")
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_SECONDS, help="Seconds between append batches")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed for reproducibility")
    parser.add_argument("--out-prefix", type=str, default=DEFAULT_OUT_PREFIX, help="Output filename prefix (CSV and NDJSON)")
    args = parser.parse_args()

    # Set RNG seeds when reproducibility is required for testing
    if args.seed is not None:
        random.seed(args.seed)
        if np:
            np.random.seed(args.seed)
        Faker.seed(args.seed)

    run_loop(args.n_per_interval, args.interval, args.out_prefix)

if __name__ == "__main__":
    main()
