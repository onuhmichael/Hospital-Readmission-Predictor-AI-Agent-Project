# 🏥 Hospital Readmission Predictor AI Agent

## 📌 Project Description
This project is a **proof-of-concept** demonstrating how to build, deploy, and manage an **AI agent** capable of predicting **30-day hospital readmissions**.  

The workflow is designed to run on the **Azure AI Foundry** platform, emphasizing a **minimal, production-minded MVP (Minimum Viable Product)** approach.  

The goal is to create a **practical, end-to-end solution** that:
- Starts with **synthetic data generation**  
- Moves through **model training and deployment**  
- Culminates in an **intelligent agent** for clinical decision support  

This repository serves as both a **comprehensive guide** and a **showcase** for leveraging modern AI platforms to improve **patient outcomes**.

---

## 📑 Table of Contents
- [Project Goals](#-project-goals)  
- [Tech Stack](#-tech-stack)  
- [Roadmap](#-roadmap)  
- [Synthetic Data Generator](#-synthetic-data-generator)  
  - [Features](#-features)  
  - [Configuration](#-configuration)  
  - [Data Schema](#-data-schema)  
  - [Usage](#-usage)  
  - [Output Example](#-output-example)  
  - [Customization Ideas](#-customization-ideas)  
- [Documentation](#-documentation)  
- [Contributing](#-contributing)  
- [License](#-license)  
- [Acknowledgements](#-acknowledgements)  

---

## 🎯 Project Goals
The primary objectives of this project are:

1. **Establish a Structured Workflow**  
   - Set up a clean, manageable project structure using **GitHub** for version control  
   - Use a **Kanban board** for agile task management  

2. **Generate Realistic Synthetic Data**  
   - Create a synthetic dataset that mimics real-world patient data  
   - Enable model development without compromising patient privacy  

3. **Develop a Predictive Model**  
   - Train and evaluate machine learning models  
   - Start with a simple baseline, then progress to an advanced **XGBoost model**  
   - Predict the likelihood of a patient being readmitted within 30 days of discharge  

4. **Deploy on Azure**  
   - Deploy the trained model as a **real-time, scalable endpoint**  
   - Use **Azure Machine Learning** and **Azure AI Foundry**  

5. **Build an AI Agent**  
   - Construct an AI agent in **Azure AI Foundry**  
   - Integrate the deployed model as a tool  
   - Provide **clear, actionable risk assessments** for clinical decision support  

6. **Showcase and Document**  
   - Thoroughly document every step of the process  
   - Create a valuable reference for building similar AI solutions in healthcare  

---

## 🛠️ Tech Stack
- **Azure AI Foundry**  
- **Azure Machine Learning**  
- **Python (scikit-learn, XGBoost, Pandas, NumPy)**  
- **GitHub Projects (Kanban)**  

---

## 🚀 Roadmap
- [ ] Define project structure & GitHub Kanban board  
- [ ] Generate synthetic patient dataset  
- [ ] Train baseline ML model  
- [ ] Implement XGBoost model for improved accuracy  
- [ ] Deploy model to Azure ML endpoint  
- [ ] Build AI agent in Azure AI Foundry  
- [ ] Document full workflow with examples  

---

## 🧪 Synthetic Data Generator

The **Hospital Readmission Synthetic Data Generator** is the foundation of this project. It produces realistic, privacy-safe patient records that fuel model training and evaluation.

### 📌 Features
- **Continuous Data Streaming**: Generates batches of patient records at configurable time intervals.  
- **Extended Realism**: Includes demographics, clinical details, lifestyle factors, and insurance information.  
- **Customizable Output**: Easily adjust batch size, interval, and output directory.  
- **CSV Export**: Appends new records to a CSV file for downstream use.  
- **Safe & Synthetic**: No real patient data is used—records are fully artificial.  

---

### ⚙️ Configuration
At the top of the script, you can configure:

```python
OUTPUT_DIR = r"C:\Hospital Readmission Predictor AI Agent Project\HRPA_Data"
OUTPUT_FILE = "hospital_readmission_data.csv"
BATCH_SIZE = 10   # number of records generated every cycle
INTERVAL = 2      # seconds between each batch
```

- **OUTPUT_DIR** → Directory where the CSV file will be saved  
- **OUTPUT_FILE** → Name of the CSV file  
- **BATCH_SIZE** → Number of records generated per cycle  
- **INTERVAL** → Time (in seconds) between each batch  

---

### 📊 Data Schema

| Field                        | Description |
|-------------------------------|-------------|
| PatientID                     | Unique patient identifier (UUID-based) |
| Age                           | Patient age (18–90) |
| Gender                        | Male, Female, or Other |
| AdmissionDate                 | Date of hospital admission |
| DischargeDate                 | Date of discharge |
| Diagnosis                     | Primary diagnosis (e.g., Heart Failure, Diabetes) |
| LengthOfStay                  | Number of days admitted |
| PriorAdmissions               | Count of previous admissions |
| Medications                   | Example prescribed medication |
| ReadmittedWithin30Days        | Target variable (0 = No, 1 = Yes) |
| BMI                           | Body Mass Index (18.0–40.0) |
| SmokingStatus                 | Never, Former, or Current |
| AlcoholUse                    | None, Moderate, or Heavy |
| BloodPressure                 | Systolic/Diastolic (e.g., 120/80) |
| CholesterolLevel              | Cholesterol in mg/dL (150–300) |
| HbA1c                         | Glycated hemoglobin % (4.5–12.0) |
| FollowUpAppointmentScheduled  | 0 = No, 1 = Yes |
| InsuranceType                 | Public, Private, or Self-Pay |
| RecordGeneratedAt             | Timestamp of record creation |

---

### 🚀 Usage

1. **Install dependencies**  
   ```bash
   pip install pandas
   ```

2. **Run the generator**  
   ```bash
   python hospital_readmission_generator.py
   ```

3. **Stop the generator**  
   Press `CTRL + C` to stop streaming data.  

---

### 📂 Output Example

```csv
PatientID,Age,Gender,AdmissionDate,DischargeDate,Diagnosis,LengthOfStay,PriorAdmissions,Medications,ReadmittedWithin30Days,BMI,SmokingStatus,AlcoholUse,BloodPressure,CholesterolLevel,HbA1c,FollowUpAppointmentScheduled,InsuranceType,RecordGeneratedAt
a1b2c3d4,67,Female,2025-03-15,2025-03-20,Heart Failure,5,2,Beta Blockers,1,29.4,Former,Moderate,135/85,210,7.2,1,Public,2025-09-28 15:20:45
```

---

### 🔧 Customization Ideas
- Add **more diagnoses or medications** to expand realism  
- Introduce **geographic or hospital-specific fields**  
- Simulate **seasonal admission trends**  
- Integrate with **streaming platforms** (Kafka, Event Hubs)  

---

## 📖 Documentation
Detailed documentation will be provided in the `/docs` folder, including:
- Data generation process  
- Model training & evaluation  
- Deployment instructions  
- AI agent integration  

---

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request with improvements or new features.  

---

## 📜 License
This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.  

---

## 🌟 Acknowledgements
- Inspired by the need to improve **patient outcomes** through **AI-driven healthcare solutions**  
- Built with **Azure AI Foundry** and **Azure Machine Learning**  
