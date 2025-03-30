#!/bin/bash

# This script sets up CloudWatch-compatible monitoring for the Telemedicine Appointment Data Pipeline
# It creates a cron job to run the monitoring system periodically

# Set up environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITORING_SCRIPT="${SCRIPT_DIR}/../scripts/monitoring_system.py"
LOG_DIR="${SCRIPT_DIR}/../logs"
CRON_FILE="${SCRIPT_DIR}/../config/monitoring_cron"

# Create log directory if it doesn't exist
mkdir -p "${LOG_DIR}"

# Create cron job to run monitoring system every 15 minutes
echo "# Telemedicine Pipeline Monitoring - runs every 15 minutes" > "${CRON_FILE}"
echo "*/15 * * * * python3 ${MONITORING_SCRIPT} >> ${LOG_DIR}/cron_monitoring.log 2>&1" >> "${CRON_FILE}"

# Install cron job
crontab "${CRON_FILE}"

echo "Monitoring system has been set up to run every 15 minutes."
echo "Cron job installed from: ${CRON_FILE}"
echo "Logs will be written to: ${LOG_DIR}/cron_monitoring.log"

# Run monitoring system once to verify it works
echo "Running monitoring system for initial verification..."
python3 "${MONITORING_SCRIPT}"

echo "Monitoring setup complete!"
