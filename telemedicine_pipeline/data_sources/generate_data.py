import pandas as pd
import numpy as np
import json
import os
import random
from datetime import datetime, timedelta
import uuid

# Set random seed for reproducibility
np.random.seed(42)

# Constants
NUM_PROVIDERS = 50
NUM_PATIENTS = 500
NUM_APPOINTMENTS = 2000
NUM_FEEDBACK = 1500
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 3, 30)

# Helper functions
def random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def random_time():
    hours = random.randint(8, 17)
    minutes = random.choice([0, 15, 30, 45])
    return f"{hours:02d}:{minutes:02d}:00"

# Generate provider data
def generate_provider_data():
    specialties = [
        "Family Medicine", "Internal Medicine", "Pediatrics", "Cardiology",
        "Dermatology", "Neurology", "Psychiatry", "Orthopedics", 
        "Obstetrics/Gynecology", "Ophthalmology", "Oncology", "Urology"
    ]
    
    states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]
    
    providers = []
    
    for i in range(1, NUM_PROVIDERS + 1):
        provider_id = f"PROV{i:04d}"
        first_name = f"Provider{i}"
        last_name = f"Doctor{i}"
        specialty = random.choice(specialties)
        years_experience = random.randint(1, 30)
        state = random.choice(states)
        hourly_rate = round(random.uniform(100, 500), 2)
        available_hours = random.randint(20, 40)
        
        provider = {
            "provider_id": provider_id,
            "first_name": first_name,
            "last_name": last_name,
            "specialty": specialty,
            "years_experience": years_experience,
            "state": state,
            "hourly_rate": hourly_rate,
            "available_hours": available_hours,
            "active": random.random() > 0.1  # 90% are active
        }
        
        providers.append(provider)
    
    return pd.DataFrame(providers)

# Generate patient data
def generate_patient_data():
    patients = []
    
    for i in range(1, NUM_PATIENTS + 1):
        patient_id = f"PAT{i:06d}"
        age = random.randint(18, 85)
        gender = random.choice(["Male", "Female", "Other"])
        
        patient = {
            "patient_id": patient_id,
            "age": age,
            "gender": gender,
            "has_insurance": random.random() > 0.2,  # 80% have insurance
            "registration_date": random_date(START_DATE - timedelta(days=365), END_DATE).strftime("%Y-%m-%d")
        }
        
        patients.append(patient)
    
    return pd.DataFrame(patients)

# Generate appointment logs
def generate_appointment_logs(providers_df, patients_df):
    appointment_statuses = ["Completed", "Cancelled", "No-show", "Rescheduled"]
    appointment_types = ["Initial Consultation", "Follow-up", "Urgent Care", "Specialist Referral", "Medication Review"]
    device_types = ["Mobile Phone", "Tablet", "Laptop", "Desktop"]
    operating_systems = ["iOS", "Android", "Windows", "macOS", "Linux"]
    browsers = ["Chrome", "Safari", "Firefox", "Edge"]
    
    appointments = []
    
    provider_ids = providers_df["provider_id"].tolist()
    patient_ids = patients_df["patient_id"].tolist()
    
    for i in range(NUM_APPOINTMENTS):
        appointment_id = str(uuid.uuid4())
        provider_id = random.choice(provider_ids)
        patient_id = random.choice(patient_ids)
        
        appointment_date = random_date(START_DATE, END_DATE)
        scheduled_time = random_time()
        
        # Generate random wait time (0-30 minutes)
        wait_time_minutes = random.randint(0, 30)
        
        # Generate random appointment duration (10-60 minutes)
        duration_minutes = random.randint(10, 60)
        
        status = random.choices(
            appointment_statuses, 
            weights=[0.75, 0.1, 0.05, 0.1],  # 75% completed, 10% cancelled, 5% no-show, 10% rescheduled
            k=1
        )[0]
        
        # Device and connection info
        device_type = random.choice(device_types)
        os = random.choice(operating_systems)
        browser = random.choice(browsers)
        connection_quality = random.choice(["Excellent", "Good", "Fair", "Poor"])
        
        # Technical issues
        had_technical_issues = random.random() < 0.15  # 15% have technical issues
        technical_issue_type = None
        if had_technical_issues:
            technical_issue_type = random.choice([
                "Audio Problems", "Video Problems", "Connection Lost", 
                "Login Issues", "App Crash", "Browser Compatibility"
            ])
        
        appointment = {
            "appointment_id": appointment_id,
            "provider_id": provider_id,
            "patient_id": patient_id,
            "appointment_date": appointment_date.strftime("%Y-%m-%d"),
            "scheduled_time": scheduled_time,
            "appointment_type": random.choice(appointment_types),
            "status": status,
            "wait_time_minutes": wait_time_minutes if status != "No-show" else None,
            "duration_minutes": duration_minutes if status == "Completed" else None,
            "device_type": device_type,
            "operating_system": os,
            "browser": browser,
            "connection_quality": connection_quality,
            "had_technical_issues": had_technical_issues,
            "technical_issue_type": technical_issue_type,
            "timestamp": (appointment_date + timedelta(minutes=random.randint(0, 1440))).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        appointments.append(appointment)
    
    return pd.DataFrame(appointments)

# Generate patient feedback
def generate_patient_feedback(appointment_logs_df):
    # Only generate feedback for completed appointments
    completed_appointments = appointment_logs_df[appointment_logs_df["status"] == "Completed"]
    
    # Randomly select appointments to have feedback (not all appointments get feedback)
    feedback_appointments = completed_appointments.sample(min(NUM_FEEDBACK, len(completed_appointments)))
    
    feedback_data = []
    
    for _, appointment in feedback_appointments.iterrows():
        # Generate feedback 1-3 days after appointment
        appointment_date = datetime.strptime(appointment["appointment_date"], "%Y-%m-%d")
        feedback_date = appointment_date + timedelta(days=random.randint(1, 3))
        
        # Generate ratings (1-5 scale)
        provider_rating = max(1, min(5, int(np.random.normal(4.2, 0.8))))
        ease_of_use_rating = max(1, min(5, int(np.random.normal(3.8, 1.0))))
        audio_quality_rating = max(1, min(5, int(np.random.normal(3.9, 0.9))))
        video_quality_rating = max(1, min(5, int(np.random.normal(3.7, 1.1))))
        overall_satisfaction = max(1, min(5, int(np.random.normal(4.0, 0.9))))
        
        # Lower ratings if there were technical issues
        if appointment["had_technical_issues"]:
            ease_of_use_rating = max(1, ease_of_use_rating - random.randint(1, 2))
            audio_quality_rating = max(1, audio_quality_rating - random.randint(1, 2))
            video_quality_rating = max(1, video_quality_rating - random.randint(1, 2))
            overall_satisfaction = max(1, overall_satisfaction - random.randint(1, 2))
        
        # Generate comments based on ratings
        comments = []
        if overall_satisfaction >= 4:
            comments.append(random.choice([
                "Great experience overall!",
                "The doctor was very helpful and professional.",
                "I appreciate the convenience of telemedicine.",
                "Much better than going to a physical office.",
                "Will definitely use this service again."
            ]))
        elif overall_satisfaction <= 2:
            comments.append(random.choice([
                "The connection was poor and made it difficult to communicate.",
                "I had trouble logging in and wasted time.",
                "The doctor seemed rushed and didn't address all my concerns.",
                "The app kept crashing during my appointment.",
                "I prefer in-person visits for better care."
            ]))
        
        feedback = {
            "feedback_id": str(uuid.uuid4()),
            "appointment_id": appointment["appointment_id"],
            "patient_id": appointment["patient_id"],
            "provider_id": appointment["provider_id"],
            "feedback_date": feedback_date.strftime("%Y-%m-%d"),
            "provider_rating": provider_rating,
            "ease_of_use_rating": ease_of_use_rating,
            "audio_quality_rating": audio_quality_rating,
            "video_quality_rating": video_quality_rating,
            "overall_satisfaction": overall_satisfaction,
            "would_recommend": overall_satisfaction >= 4,
            "comments": " ".join(comments) if comments else None,
            "timestamp": feedback_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        feedback_data.append(feedback)
    
    return pd.DataFrame(feedback_data)

# Main function to generate all data
def generate_all_data():
    print("Generating provider data...")
    providers_df = generate_provider_data()
    
    print("Generating patient data...")
    patients_df = generate_patient_data()
    
    print("Generating appointment logs...")
    appointment_logs_df = generate_appointment_logs(providers_df, patients_df)
    
    print("Generating patient feedback...")
    feedback_df = generate_patient_feedback(appointment_logs_df)
    
    # Create directories if they don't exist
    os.makedirs("data_sources/provider_data", exist_ok=True)
    os.makedirs("data_sources/patient_feedback", exist_ok=True)
    os.makedirs("data_sources/appointment_logs", exist_ok=True)
    
    # Save provider data as CSV (simulating RDS data)
    providers_df.to_csv("data_sources/provider_data/providers.csv", index=False)
    patients_df.to_csv("data_sources/provider_data/patients.csv", index=False)
    
    # Save appointment logs as JSON files (simulating streaming data)
    for _, appointment in appointment_logs_df.iterrows():
        appointment_date = appointment["appointment_date"]
        filename = f"data_sources/appointment_logs/appointment_{appointment['appointment_id']}.json"
        with open(filename, 'w') as f:
            json.dump(appointment.to_dict(), f, indent=2)
    
    # Save appointment logs as a single file for easier processing
    appointment_logs_df.to_csv("data_sources/appointment_logs/appointment_logs.csv", index=False)
    
    # Save patient feedback as JSON files (simulating S3 data)
    for _, feedback in feedback_df.iterrows():
        feedback_date = feedback["feedback_date"]
        filename = f"data_sources/patient_feedback/feedback_{feedback['feedback_id']}.json"
        with open(filename, 'w') as f:
            json.dump(feedback.to_dict(), f, indent=2)
    
    # Save feedback as a single file for easier processing
    feedback_df.to_csv("data_sources/patient_feedback/patient_feedback.csv", index=False)
    
    print("Data generation complete!")
    print(f"Generated {len(providers_df)} providers")
    print(f"Generated {len(patients_df)} patients")
    print(f"Generated {len(appointment_logs_df)} appointment logs")
    print(f"Generated {len(feedback_df)} patient feedback records")

if __name__ == "__main__":
    generate_all_data()
