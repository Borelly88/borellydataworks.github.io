-- Redshift compatible schema for Telemedicine Appointment Data Pipeline
-- This script creates the dimensional model in a Redshift-compatible PostgreSQL database

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS fact_feedback;
DROP TABLE IF EXISTS fact_appointment;
DROP TABLE IF EXISTS dim_patient;
DROP TABLE IF EXISTS dim_provider;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_time;
DROP TABLE IF EXISTS dim_status;
DROP TABLE IF EXISTS dim_device;

-- Create dimension tables
CREATE TABLE dim_date (
    date_id VARCHAR(8) PRIMARY KEY,
    date DATE NOT NULL,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(10) NOT NULL,
    month_name VARCHAR(10) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL
) DISTSTYLE ALL;

CREATE TABLE dim_time (
    time_id VARCHAR(4) PRIMARY KEY,
    time_value VARCHAR(8) NOT NULL,
    hour INTEGER NOT NULL,
    minute INTEGER NOT NULL,
    am_pm VARCHAR(2) NOT NULL,
    hour_12 INTEGER NOT NULL,
    day_period VARCHAR(15) NOT NULL
) DISTSTYLE ALL;

CREATE TABLE dim_provider (
    provider_key INTEGER PRIMARY KEY,
    provider_id VARCHAR(10) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    years_experience INTEGER NOT NULL,
    state VARCHAR(2) NOT NULL,
    hourly_rate DECIMAL(10, 2) NOT NULL,
    available_hours INTEGER NOT NULL,
    active BOOLEAN NOT NULL
) DISTSTYLE ALL;

CREATE TABLE dim_patient (
    patient_key INTEGER PRIMARY KEY,
    patient_id VARCHAR(10) NOT NULL,
    age INTEGER NOT NULL,
    age_group VARCHAR(10) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    has_insurance BOOLEAN NOT NULL,
    registration_date DATE NOT NULL
) DISTSTYLE ALL;

CREATE TABLE dim_status (
    status_key INTEGER PRIMARY KEY,
    status VARCHAR(20) NOT NULL,
    is_successful BOOLEAN NOT NULL
) DISTSTYLE ALL;

CREATE TABLE dim_device (
    device_key INTEGER PRIMARY KEY,
    device_type VARCHAR(20) NOT NULL,
    is_mobile BOOLEAN NOT NULL
) DISTSTYLE ALL;

-- Create fact tables
CREATE TABLE fact_appointment (
    appointment_id VARCHAR(36) PRIMARY KEY,
    provider_key INTEGER REFERENCES dim_provider(provider_key),
    patient_key INTEGER REFERENCES dim_patient(patient_key),
    date_id VARCHAR(8) REFERENCES dim_date(date_id),
    time_id VARCHAR(4) REFERENCES dim_time(time_id),
    status_key INTEGER REFERENCES dim_status(status_key),
    device_key INTEGER REFERENCES dim_device(device_key),
    appointment_type VARCHAR(100) NOT NULL,
    wait_time_minutes INTEGER,
    duration_minutes INTEGER,
    connection_quality VARCHAR(20),
    had_technical_issues BOOLEAN,
    technical_issue_type VARCHAR(100),
    timestamp TIMESTAMP
) DISTKEY(date_id) SORTKEY(date_id, time_id);

CREATE TABLE fact_feedback (
    feedback_id VARCHAR(36) PRIMARY KEY,
    appointment_id VARCHAR(36) REFERENCES fact_appointment(appointment_id),
    provider_key INTEGER REFERENCES dim_provider(provider_key),
    patient_key INTEGER REFERENCES dim_patient(patient_key),
    date_id VARCHAR(8) REFERENCES dim_date(date_id),
    provider_rating INTEGER,
    ease_of_use_rating INTEGER,
    audio_quality_rating INTEGER,
    video_quality_rating INTEGER,
    overall_satisfaction INTEGER,
    would_recommend BOOLEAN,
    comments TEXT,
    timestamp TIMESTAMP
) DISTKEY(date_id) SORTKEY(date_id);

-- Create indexes for better query performance
CREATE INDEX idx_appointment_provider ON fact_appointment(provider_key);
CREATE INDEX idx_appointment_patient ON fact_appointment(patient_key);
CREATE INDEX idx_appointment_status ON fact_appointment(status_key);
CREATE INDEX idx_appointment_device ON fact_appointment(device_key);

CREATE INDEX idx_feedback_appointment ON fact_feedback(appointment_id);
CREATE INDEX idx_feedback_provider ON fact_feedback(provider_key);
CREATE INDEX idx_feedback_patient ON fact_feedback(patient_key);
