import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Define paths - updated to use the correct nested data source paths
DATA_SOURCES_DIR = '/home/ubuntu/telemedicine_pipeline/data_sources/data_sources'
OUTPUT_DIR = '/home/ubuntu/telemedicine_pipeline/data_processing/transformed'

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_appointment_data():
    """Load appointment data from original data sources"""
    appointment_file = os.path.join(DATA_SOURCES_DIR, 'appointment_logs/appointment_logs.csv')
    
    if not os.path.exists(appointment_file):
        print(f"Appointment data file not found: {appointment_file}")
        return pd.DataFrame()
    
    appointments_df = pd.read_csv(appointment_file)
    print(f"Loaded {len(appointments_df)} appointments from original data source")
    return appointments_df

def load_feedback_data():
    """Load feedback data from original data sources"""
    feedback_file = os.path.join(DATA_SOURCES_DIR, 'patient_feedback/patient_feedback.csv')
    
    if not os.path.exists(feedback_file):
        print(f"Feedback data file not found: {feedback_file}")
        return pd.DataFrame()
    
    feedback_df = pd.read_csv(feedback_file)
    print(f"Loaded {len(feedback_df)} feedback records from original data source")
    return feedback_df

def load_provider_data():
    """Load provider data from original data sources"""
    provider_file = os.path.join(DATA_SOURCES_DIR, 'provider_data/providers.csv')
    
    if not os.path.exists(provider_file):
        print(f"Provider data file not found: {provider_file}")
        return pd.DataFrame()
    
    providers_df = pd.read_csv(provider_file)
    print(f"Loaded {len(providers_df)} providers from original data source")
    return providers_df

def load_patient_data():
    """Load patient data from original data sources"""
    patient_file = os.path.join(DATA_SOURCES_DIR, 'provider_data/patients.csv')
    
    if not os.path.exists(patient_file):
        print(f"Patient data file not found: {patient_file}")
        return pd.DataFrame()
    
    patients_df = pd.read_csv(patient_file)
    print(f"Loaded {len(patients_df)} patients from original data source")
    return patients_df

def transform_date_dimensions(appointments_df):
    """Create date dimension table from appointment data"""
    if appointments_df.empty:
        print("No appointment data available for date dimension")
        return pd.DataFrame()
    
    # Extract unique dates from appointments
    dates = pd.to_datetime(appointments_df['appointment_date'].unique())
    
    # Create date range that covers all appointments
    min_date = dates.min()
    max_date = dates.max()
    
    # Add buffer before and after
    date_range = pd.date_range(
        start=min_date - timedelta(days=30),
        end=max_date + timedelta(days=30),
        freq='D'
    )
    
    # Create date dimension table
    date_dim = pd.DataFrame({
        'date_id': date_range.strftime('%Y%m%d'),
        'date': date_range,
        'day': date_range.day,
        'month': date_range.month,
        'year': date_range.year,
        'quarter': date_range.quarter,
        'day_of_week': date_range.dayofweek,
        'day_name': date_range.strftime('%A'),
        'month_name': date_range.strftime('%B'),
        'is_weekend': date_range.dayofweek.isin([5, 6]),
        'is_holiday': False  # Placeholder, would need holiday calendar to populate
    })
    
    print(f"Created date dimension with {len(date_dim)} rows")
    return date_dim

def transform_time_dimensions(appointments_df):
    """Create time dimension table from appointment data"""
    if appointments_df.empty:
        print("No appointment data available for time dimension")
        return pd.DataFrame()
    
    # Create time range with 15-minute intervals
    time_range = pd.date_range(
        start='00:00:00',
        end='23:59:59',
        freq='15min'
    ).time
    
    # Create time dimension table
    time_dim = pd.DataFrame({
        'time_id': [f"{t.hour:02d}{t.minute:02d}" for t in time_range],
        'time_value': [f"{t.hour:02d}:{t.minute:02d}:00" for t in time_range],
        'hour': [t.hour for t in time_range],
        'minute': [t.minute for t in time_range],
        'am_pm': ['AM' if t.hour < 12 else 'PM' for t in time_range],
        'hour_12': [(t.hour % 12) if (t.hour % 12) != 0 else 12 for t in time_range],
        'day_period': [
            'Early Morning' if t.hour < 6 else
            'Morning' if t.hour < 12 else
            'Afternoon' if t.hour < 17 else
            'Evening' if t.hour < 21 else
            'Night'
            for t in time_range
        ]
    })
    
    print(f"Created time dimension with {len(time_dim)} rows")
    return time_dim

def transform_provider_dimension(providers_df):
    """Transform provider data into dimension table"""
    if providers_df.empty:
        print("No provider data available")
        return pd.DataFrame()
    
    # Create provider dimension table
    provider_dim = providers_df.copy()
    
    # Add surrogate key
    provider_dim['provider_key'] = provider_dim.index + 1
    
    # Reorder columns
    provider_dim = provider_dim[[
        'provider_key', 'provider_id', 'first_name', 'last_name', 
        'specialty', 'years_experience', 'state', 'hourly_rate', 
        'available_hours', 'active'
    ]]
    
    print(f"Created provider dimension with {len(provider_dim)} rows")
    return provider_dim

def transform_patient_dimension(patients_df):
    """Transform patient data into dimension table"""
    if patients_df.empty:
        print("No patient data available")
        return pd.DataFrame()
    
    # Create patient dimension table
    patient_dim = patients_df.copy()
    
    # Add surrogate key
    patient_dim['patient_key'] = patient_dim.index + 1
    
    # Add age group
    patient_dim['age_group'] = pd.cut(
        patient_dim['age'],
        bins=[0, 18, 35, 50, 65, 100],
        labels=['Under 18', '18-34', '35-49', '50-64', '65+']
    )
    
    # Reorder columns
    patient_dim = patient_dim[[
        'patient_key', 'patient_id', 'age', 'age_group', 
        'gender', 'has_insurance', 'registration_date'
    ]]
    
    print(f"Created patient dimension with {len(patient_dim)} rows")
    return patient_dim

def transform_appointment_fact(appointments_df, provider_dim, patient_dim, date_dim, time_dim):
    """Transform appointment data into fact table"""
    if appointments_df.empty:
        print("No appointment data available")
        return pd.DataFrame()
    
    # Create appointment fact table
    appointment_fact = appointments_df.copy()
    
    # Convert date and time columns
    appointment_fact['appointment_date'] = pd.to_datetime(appointment_fact['appointment_date'])
    
    # Create date_id
    appointment_fact['date_id'] = appointment_fact['appointment_date'].dt.strftime('%Y%m%d')
    
    # Create time_id
    def extract_time_id(time_str):
        if pd.isna(time_str):
            return None
        try:
            hour, minute, _ = time_str.split(':')
            return f"{int(hour):02d}{int(minute):02d}"
        except:
            return None
    
    appointment_fact['time_id'] = appointment_fact['scheduled_time'].apply(extract_time_id)
    
    # Join with dimension tables to get surrogate keys
    if not provider_dim.empty:
        provider_keys = provider_dim[['provider_id', 'provider_key']].set_index('provider_id')
        appointment_fact = appointment_fact.join(provider_keys, on='provider_id')
    else:
        appointment_fact['provider_key'] = None
    
    if not patient_dim.empty:
        patient_keys = patient_dim[['patient_id', 'patient_key']].set_index('patient_id')
        appointment_fact = appointment_fact.join(patient_keys, on='patient_id')
    else:
        appointment_fact['patient_key'] = None
    
    # Add status dimension
    status_mapping = {
        'Completed': 1,
        'Cancelled': 2,
        'No-show': 3,
        'Rescheduled': 4
    }
    appointment_fact['status_key'] = appointment_fact['status'].map(status_mapping)
    
    # Add device type dimension
    device_mapping = {
        'Mobile Phone': 1,
        'Tablet': 2,
        'Laptop': 3,
        'Desktop': 4
    }
    appointment_fact['device_key'] = appointment_fact['device_type'].map(device_mapping)
    
    # Add measures
    appointment_fact['wait_time_minutes'] = appointment_fact['wait_time_minutes'].fillna(0)
    appointment_fact['duration_minutes'] = appointment_fact['duration_minutes'].fillna(0)
    appointment_fact['had_technical_issues'] = appointment_fact['had_technical_issues'].fillna(False)
    
    # Select and rename columns for fact table
    appointment_fact = appointment_fact[[
        'appointment_id', 'provider_key', 'patient_key', 'date_id', 'time_id',
        'status_key', 'device_key', 'appointment_type', 'wait_time_minutes', 
        'duration_minutes', 'connection_quality', 'had_technical_issues', 
        'technical_issue_type', 'timestamp'
    ]]
    
    print(f"Created appointment fact table with {len(appointment_fact)} rows")
    return appointment_fact

def transform_feedback_fact(feedback_df, provider_dim, patient_dim, appointment_fact):
    """Transform feedback data into fact table"""
    if feedback_df.empty:
        print("No feedback data available")
        return pd.DataFrame()
    
    # Create feedback fact table
    feedback_fact = feedback_df.copy()
    
    # Convert date column
    feedback_fact['feedback_date'] = pd.to_datetime(feedback_fact['feedback_date'])
    
    # Create date_id
    feedback_fact['date_id'] = feedback_fact['feedback_date'].dt.strftime('%Y%m%d')
    
    # Join with dimension tables to get surrogate keys
    if not provider_dim.empty:
        provider_keys = provider_dim[['provider_id', 'provider_key']].set_index('provider_id')
        feedback_fact = feedback_fact.join(provider_keys, on='provider_id')
    else:
        feedback_fact['provider_key'] = None
    
    if not patient_dim.empty:
        patient_keys = patient_dim[['patient_id', 'patient_key']].set_index('patient_id')
        feedback_fact = feedback_fact.join(patient_keys, on='patient_id')
    else:
        feedback_fact['patient_key'] = None
    
    # Add measures
    feedback_fact['provider_rating'] = feedback_fact['provider_rating'].fillna(0)
    feedback_fact['ease_of_use_rating'] = feedback_fact['ease_of_use_rating'].fillna(0)
    feedback_fact['audio_quality_rating'] = feedback_fact['audio_quality_rating'].fillna(0)
    feedback_fact['video_quality_rating'] = feedback_fact['video_quality_rating'].fillna(0)
    feedback_fact['overall_satisfaction'] = feedback_fact['overall_satisfaction'].fillna(0)
    feedback_fact['would_recommend'] = feedback_fact['would_recommend'].fillna(False)
    
    # Select and rename columns for fact table
    feedback_fact = feedback_fact[[
        'feedback_id', 'appointment_id', 'provider_key', 'patient_key', 'date_id',
        'provider_rating', 'ease_of_use_rating', 'audio_quality_rating',
        'video_quality_rating', 'overall_satisfaction', 'would_recommend',
        'comments', 'timestamp'
    ]]
    
    print(f"Created feedback fact table with {len(feedback_fact)} rows")
    return feedback_fact

def main():
    # Load data
    print("Loading data...")
    appointments_df = load_appointment_data()
    feedback_df = load_feedback_data()
    providers_df = load_provider_data()
    patients_df = load_patient_data()
    
    # Transform dimension tables
    print("\nTransforming dimension tables...")
    date_dim = transform_date_dimensions(appointments_df)
    time_dim = transform_time_dimensions(appointments_df)
    provider_dim = transform_provider_dimension(providers_df)
    patient_dim = transform_patient_dimension(patients_df)
    
    # Transform fact tables
    print("\nTransforming fact tables...")
    appointment_fact = transform_appointment_fact(
        appointments_df, provider_dim, patient_dim, date_dim, time_dim
    )
    feedback_fact = transform_feedback_fact(
        feedback_df, provider_dim, patient_dim, appointment_fact
    )
    
    # Save transformed data
    print("\nSaving transformed data...")
    
    # Save dimension tables
    date_dim.to_csv(os.path.join(OUTPUT_DIR, 'dim_date.csv'), index=False)
    time_dim.to_csv(os.path.join(OUTPUT_DIR, 'dim_time.csv'), index=False)
    provider_dim.to_csv(os.path.join(OUTPUT_DIR, 'dim_provider.csv'), index=False)
    patient_dim.to_csv(os.path.join(OUTPUT_DIR, 'dim_patient.csv'), index=False)
    
    # Create status dimension
    status_dim = pd.DataFrame({
        'status_key': [1, 2, 3, 4],
        'status': ['Completed', 'Cancelled', 'No-show', 'Rescheduled'],
        'is_successful': [True, False, False, False]
    })
    status_dim.to_csv(os.path.join(OUTPUT_DIR, 'dim_status.csv'), index=False)
    
    # Create device dimension
    device_dim = pd.DataFrame({
        'device_key': [1, 2, 3, 4],
        'device_type': ['Mobile Phone', 'Tablet', 'Laptop', 'Desktop'],
        'is_mobile': [True, True, False, False]
    })
    device_dim.to_csv(os.path.join(OUTPUT_DIR, 'dim_device.csv'), index=False)
    
    # Save fact tables
    appointment_fact.to_csv(os.path.join(OUTPUT_DIR, 'fact_appointment.csv'), index=False)
    feedback_fact.to_csv(os.path.join(OUTPUT_DIR, 'fact_feedback.csv'), index=False)
    
    print("\nData transformation complete!")
    print(f"Transformed data saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
