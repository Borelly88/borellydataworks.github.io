#!/bin/bash

# Setup script for Telemedicine Appointment Data Pipeline
# This script initializes the local development environment

echo "Setting up Telemedicine Appointment Data Pipeline environment..."

# Create necessary directories if they don't exist
mkdir -p data_sources/appointment_logs
mkdir -p data_sources/patient_feedback
mkdir -p data_sources/provider_data
mkdir -p data_ingestion/airflow/dags
mkdir -p data_ingestion/airflow/logs
mkdir -p data_ingestion/airflow/plugins
mkdir -p data_ingestion/kafka
mkdir -p data_processing/etl
mkdir -p data_processing/models
mkdir -p data_warehouse/schemas
mkdir -p data_warehouse/scripts
mkdir -p visualization/dashboards
mkdir -p monitoring/alerts

# Add PATH for local Python packages
echo 'export PATH=$PATH:$HOME/.local/bin' >> ~/.bashrc
export PATH=$PATH:$HOME/.local/bin

# Initialize local environment
echo "Initializing local environment variables..."
source .env

echo "Setup complete! You can now start the services using docker-compose up"
