import os
import time
import uuid
import random
import json
import pandas as pd
from datetime import datetime, timedelta

# ============================================================
# CONFIGURATION SECTION
# ============================================================
OUTPUT_DIR = r"C:\Hospital Readmission Predictor AI Agent Project\HRPA_Data"
CSV_FILE = "hospital_readmission_data.csv"
JSONL_FILE = "hospital_readmission_data.jsonl"
BATCH_SIZE = 10   # number of records generated every cycle
INTERVAL = 2      # seconds between each batch

os.makedirs(OUTPUT_DIR, exist_ok=True)
CSV_PATH = os.path.join(OUTPUT_DIR, CSV_FILE)
JSONL_PATH = os.path.join(OUTPUT_DIR, JSONL_FILE)

# ============================================================
# SYNTHETIC DATA GENERATOR FUNCTION
# ============================================================
def generate_patient_record():
    """
    Generate one synthetic patient admission record with extended realism.
    """

    patient_id = str(uuid.uuid4())[:8]
    age = random.randint(18, 90)
    gender = random.choice(["Male", "Female", "Other"])

    admission_date = datetime.now() - timedelta(days=random.randint(0, 365))
    discharge_date = admission_date + timedelta(days=random.randint(1, 15))

    diagnosis = random.choice([
        "Heart Failure", "Pneumonia", "Diabetes", "COPD",
        "Kidney Disease", "Hypertension", "Cancer", "Stroke"
    ])
    length_of_stay = (discharge_date - admission_date).days
    prior_admissions = random.randint(0, 5)
    medications = random.choice([
        "Insulin", "Beta Blockers", "ACE Inhibitors", "Antibiotics",
        "Diuretics", "Chemotherapy", "Steroids", "Anticoagulants"
    ])
    readmitted = random.choice([0, 1])

    bmi = round(random.uniform(18.0, 40.0), 1)
    smoking_status = random.choice(["Never", "Former", "Current"])
    alcohol_use = random.choice(["None", "Moderate", "Heavy"])
    blood_pressure = f"{random.randint(100, 160)}/{random.randint(60, 100)}"
    cholesterol = random.randint(150, 300)
    hba1c = round(random.uniform(4.5, 12.0), 1)
    follow_up = random.choice([0, 1])
    insurance_type = random.choice(["Public", "Private", "Self-Pay"])

    record_generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "PatientID": patient_id,
        "Age": age,
        "Gender": gender,
        "AdmissionDate": admission_date.strftime("%Y-%m-%d"),
        "DischargeDate": discharge_date.strftime("%Y-%m-%d"),
        "Diagnosis": diagnosis,
        "LengthOfStay": length_of_stay,
        "PriorAdmissions": prior_admissions,
        "Medications": medications,
        "ReadmittedWithin30Days": readmitted,
        "BMI": bmi,
        "SmokingStatus": smoking_status,
        "AlcoholUse": alcohol_use,
        "BloodPressure": blood_pressure,
        "CholesterolLevel": cholesterol,
        "HbA1c": hba1c,
        "FollowUpAppointmentScheduled": follow_up,
        "InsuranceType": insurance_type,
        "RecordGeneratedAt": record_generated_at
    }

# ============================================================
# JSONL CONVERSION FUNCTION
# ============================================================
def convert_to_jsonl(record):
    """
    Convert a patient record into prompt-completion format
    suitable for fine-tuning in Azure AI Foundry.
    """
    prompt = (
        f"Patient {record['PatientID']} ({record['Age']} y/o {record['Gender']}) "
        f"diagnosed with {record['Diagnosis']}, admitted on {record['AdmissionDate']} "
        f"and discharged on {record['DischargeDate']}. "
        f"Clinical factors: BMI={record['BMI']}, BP={record['BloodPressure']}, "
        f"HbA1c={record['HbA1c']}, Cholesterol={record['CholesterolLevel']}, "
        f"Smoking={record['SmokingStatus']}, Alcohol={record['AlcoholUse']}. "
        f"Prior admissions={record['PriorAdmissions']}, Medications={record['Medications']}."
    )

    completion = f" ReadmittedWithin30Days: {record['ReadmittedWithin30Days']}"

    return {"prompt": prompt, "completion": completion}

# ============================================================
# VALIDATION UTILITY
# ============================================================
def validate_jsonl(file_path):
    """
    Validate that every line in the JSONL file has the required schema:
    - Must be valid JSON
    - Must contain both 'prompt' and 'completion' keys
    - Both values must be non-empty strings

    Why this matters:
    -----------------
    Azure AI Foundry expects a strict schema for fine-tuning.
    If even one line is malformed (e.g., missing 'completion'),
    the entire fine-tuning job can fail. This validator ensures
    data integrity before uploading, saving time and compute costs.
    """
    print(f"\nValidating JSONL file: {file_path}")
    errors = []
    line_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line_count += 1
            try:
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    errors.append(f"Line {i}: Not a JSON object")
                    continue
                if "prompt" not in obj or "completion" not in obj:
                    errors.append(f"Line {i}: Missing 'prompt' or 'completion'")
                    continue
                if not isinstance(obj["prompt"], str) or not isinstance(obj["completion"], str):
                    errors.append(f"Line {i}: 'prompt' and 'completion' must be strings")
                if obj["prompt"].strip() == "" or obj["completion"].strip() == "":
                    errors.append(f"Line {i}: 'prompt' or 'completion' is empty")
            except json.JSONDecodeError:
                errors.append(f"Line {i}: Invalid JSON")

    if errors:
        print("❌ Validation failed with the following issues:")
        for e in errors:
            print("   -", e)
    else:
        print(f"✅ Validation passed. {line_count} lines checked, all compliant.")

# ============================================================
# MAIN LOOP
# ============================================================
def main():
    print("Starting Synthetic Data Generator...")
    print(f"CSV will be saved in: {CSV_PATH}")
    print(f"JSONL will be saved in: {JSONL_PATH}")
    print("Press CTRL + C to stop.\n")

    if not os.path.exists(CSV_PATH):
        pd.DataFrame(columns=list(generate_patient_record().keys())).to_csv(CSV_PATH, index=False)

    if not os.path.exists(JSONL_PATH):
        open(JSONL_PATH, "w").close()

    while True:
        try:
            records = [generate_patient_record() for _ in range(BATCH_SIZE)]

            # Append to CSV
            df = pd.DataFrame(records)
            df.to_csv(CSV_PATH, mode="a", header=False, index=False)

            # Append to JSONL
            with open(JSONL_PATH, "a", encoding="utf-8") as f:
                for rec in records:
                    json_line = convert_to_jsonl(rec)
                    f.write(json.dumps(json_line) + "\n")

            print(f"Appended {BATCH_SIZE} records to both CSV and JSONL")

            # Run validation after each batch (optional, can be moved outside loop)
            validate_jsonl(JSONL_PATH)

            time.sleep(INTERVAL)

        except KeyboardInterrupt:
            print("\nData generation stopped by user.")
            break

# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    main()
