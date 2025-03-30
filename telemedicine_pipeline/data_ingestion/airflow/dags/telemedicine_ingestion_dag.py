import json
import os
import pandas as pd
from datetime import datetime, timedelta

# Airflow imports
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Default arguments for DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'telemedicine_data_ingestion',
    default_args=default_args,
    description='Ingest telemedicine data from various sources',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 3, 30),
    catchup=False,
)

# Create tables in PostgreSQL if they don't exist
create_tables = PostgresOperator(
    task_id='create_tables',
    postgres_conn_id='postgres_default',
    sql="""
    -- Provider table
    CREATE TABLE IF NOT EXISTS providers (
        provider_id VARCHAR(10) PRIMARY KEY,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        specialty VARCHAR(100),
        years_experience INTEGER,
        state VARCHAR(2),
        hourly_rate DECIMAL(10, 2),
        available_hours INTEGER,
        active BOOLEAN
    );
    
    -- Patient table
    CREATE TABLE IF NOT EXISTS patients (
        patient_id VARCHAR(10) PRIMARY KEY,
        age INTEGER,
        gender VARCHAR(10),
        has_insurance BOOLEAN,
        registration_date DATE
    );
    
    -- Appointment table
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id VARCHAR(36) PRIMARY KEY,
        provider_id VARCHAR(10) REFERENCES providers(provider_id),
        patient_id VARCHAR(10) REFERENCES patients(patient_id),
        appointment_date DATE,
        scheduled_time TIME,
        appointment_type VARCHAR(100),
        status VARCHAR(20),
        wait_time_minutes INTEGER,
        duration_minutes INTEGER,
        device_type VARCHAR(50),
        operating_system VARCHAR(50),
        browser VARCHAR(50),
        connection_quality VARCHAR(20),
        had_technical_issues BOOLEAN,
        technical_issue_type VARCHAR(100),
        timestamp TIMESTAMP
    );
    
    -- Feedback table
    CREATE TABLE IF NOT EXISTS feedback (
        feedback_id VARCHAR(36) PRIMARY KEY,
        appointment_id VARCHAR(36) REFERENCES appointments(appointment_id),
        patient_id VARCHAR(10) REFERENCES patients(patient_id),
        provider_id VARCHAR(10) REFERENCES providers(provider_id),
        feedback_date DATE,
        provider_rating INTEGER,
        ease_of_use_rating INTEGER,
        audio_quality_rating INTEGER,
        video_quality_rating INTEGER,
        overall_satisfaction INTEGER,
        would_recommend BOOLEAN,
        comments TEXT,
        timestamp TIMESTAMP
    );
    """,
    dag=dag,
)

# Function to load provider data
def load_provider_data(**kwargs):
    # Path to provider data
    provider_data_path = '/home/ubuntu/telemedicine_pipeline/data_sources/provider_data/providers.csv'
    
    # Read CSV file
    providers_df = pd.read_csv(provider_data_path)
    
    # Connect to PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE providers CASCADE;")
    
    # Insert data
    for _, row in providers_df.iterrows():
        cursor.execute(
            """
            INSERT INTO providers (
                provider_id, first_name, last_name, specialty, 
                years_experience, state, hourly_rate, available_hours, active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                row['provider_id'], row['first_name'], row['last_name'], row['specialty'],
                row['years_experience'], row['state'], row['hourly_rate'], 
                row['available_hours'], row['active']
            )
        )
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    
    return f"Loaded {len(providers_df)} provider records"

# Function to load patient data
def load_patient_data(**kwargs):
    # Path to patient data
    patient_data_path = '/home/ubuntu/telemedicine_pipeline/data_sources/provider_data/patients.csv'
    
    # Read CSV file
    patients_df = pd.read_csv(patient_data_path)
    
    # Connect to PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE patients CASCADE;")
    
    # Insert data
    for _, row in patients_df.iterrows():
        cursor.execute(
            """
            INSERT INTO patients (
                patient_id, age, gender, has_insurance, registration_date
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (
                row['patient_id'], row['age'], row['gender'],
                row['has_insurance'], row['registration_date']
            )
        )
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    
    return f"Loaded {len(patients_df)} patient records"

# Function to load appointment data
def load_appointment_data(**kwargs):
    # Path to appointment data
    appointment_data_path = '/home/ubuntu/telemedicine_pipeline/data_sources/appointment_logs/appointment_logs.csv'
    
    # Read CSV file
    appointments_df = pd.read_csv(appointment_data_path)
    
    # Connect to PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE appointments CASCADE;")
    
    # Insert data
    for _, row in appointments_df.iterrows():
        cursor.execute(
            """
            INSERT INTO appointments (
                appointment_id, provider_id, patient_id, appointment_date, 
                scheduled_time, appointment_type, status, wait_time_minutes, 
                duration_minutes, device_type, operating_system, browser, 
                connection_quality, had_technical_issues, technical_issue_type, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                row['appointment_id'], row['provider_id'], row['patient_id'], row['appointment_date'],
                row['scheduled_time'], row['appointment_type'], row['status'], row['wait_time_minutes'],
                row['duration_minutes'], row['device_type'], row['operating_system'], row['browser'],
                row['connection_quality'], row['had_technical_issues'], row['technical_issue_type'], row['timestamp']
            )
        )
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    
    return f"Loaded {len(appointments_df)} appointment records"

# Function to load feedback data
def load_feedback_data(**kwargs):
    # Path to feedback data
    feedback_data_path = '/home/ubuntu/telemedicine_pipeline/data_sources/patient_feedback/patient_feedback.csv'
    
    # Read CSV file
    feedback_df = pd.read_csv(feedback_data_path)
    
    # Connect to PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE feedback;")
    
    # Insert data
    for _, row in feedback_df.iterrows():
        cursor.execute(
            """
            INSERT INTO feedback (
                feedback_id, appointment_id, patient_id, provider_id, feedback_date,
                provider_rating, ease_of_use_rating, audio_quality_rating, 
                video_quality_rating, overall_satisfaction, would_recommend, 
                comments, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                row['feedback_id'], row['appointment_id'], row['patient_id'], row['provider_id'], 
                row['feedback_date'], row['provider_rating'], row['ease_of_use_rating'], 
                row['audio_quality_rating'], row['video_quality_rating'], row['overall_satisfaction'], 
                row['would_recommend'], row['comments'], row['timestamp']
            )
        )
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    
    return f"Loaded {len(feedback_df)} feedback records"

# Define tasks
load_providers = PythonOperator(
    task_id='load_provider_data',
    python_callable=load_provider_data,
    dag=dag,
)

load_patients = PythonOperator(
    task_id='load_patient_data',
    python_callable=load_patient_data,
    dag=dag,
)

load_appointments = PythonOperator(
    task_id='load_appointment_data',
    python_callable=load_appointment_data,
    dag=dag,
)

load_feedback = PythonOperator(
    task_id='load_feedback_data',
    python_callable=load_feedback_data,
    dag=dag,
)

# Define task dependencies
create_tables >> [load_providers, load_patients]
[load_providers, load_patients] >> load_appointments
load_appointments >> load_feedback
