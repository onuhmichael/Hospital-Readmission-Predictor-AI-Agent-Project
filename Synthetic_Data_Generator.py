import os
import time
import uuid
import random
import pandas as pd
from datetime import datetime, timedelta

# ============================================================
# CONFIGURATION SECTION
# ============================================================
OUTPUT_DIR = r"C:\Hospital Readmission Predictor AI Agent Project\HRPA_Data"
OUTPUT_FILE = "hospital_readmission_data.csv"
BATCH_SIZE = 10   # number of records generated every cycle
INTERVAL = 2      # seconds between each batch

os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

# ============================================================
# SYNTHETIC DATA GENERATOR FUNCTION
# ============================================================
def generate_patient_record():
    """
    Generate one synthetic patient admission record with extended realism.
    """

    # Unique patient identifier
    patient_id = str(uuid.uuid4())[:8]

    # Demographics
    age = random.randint(18, 90)
    gender = random.choice(["Male", "Female", "Other"])

    # Admission and discharge dates
    admission_date = datetime.now() - timedelta(days=random.randint(0, 365))
    discharge_date = admission_date + timedelta(days=random.randint(1, 15))

    # Clinical details
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
    readmitted = random.choice([0, 1])  # Target variable

    # Extra realism fields
    bmi = round(random.uniform(18.0, 40.0), 1)  # Body Mass Index
    smoking_status = random.choice(["Never", "Former", "Current"])
    alcohol_use = random.choice(["None", "Moderate", "Heavy"])
    blood_pressure = f"{random.randint(100, 160)}/{random.randint(60, 100)}"
    cholesterol = random.randint(150, 300)  # mg/dL
    hba1c = round(random.uniform(4.5, 12.0), 1)  # %
    follow_up = random.choice([0, 1])  # Was a follow-up scheduled?
    insurance_type = random.choice(["Public", "Private", "Self-Pay"])

    # Timestamp of record generation
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
# MAIN LOOP
# ============================================================
def main():
    print("Starting Synthetic Data Generator...")
    print(f"Data will be saved in: {OUTPUT_PATH}")
    print("Press CTRL + C to stop.\n")

    # If file doesn’t exist, create it with headers
    if not os.path.exists(OUTPUT_PATH):
        pd.DataFrame(columns=list(generate_patient_record().keys())).to_csv(OUTPUT_PATH, index=False)

    while True:
        try:
            records = [generate_patient_record() for _ in range(BATCH_SIZE)]
            df = pd.DataFrame(records)
            df.to_csv(OUTPUT_PATH, mode="a", header=False, index=False)
            print(f"Appended {BATCH_SIZE} records to {OUTPUT_FILE}")
            time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print("\nData generation stopped by user.")
            break

if __name__ == "__main__":
    main()
