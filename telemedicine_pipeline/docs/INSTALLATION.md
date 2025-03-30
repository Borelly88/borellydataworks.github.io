# Installation and Setup Guide for Telemedicine Appointment Data Pipeline

This guide provides detailed instructions for installing and setting up the Telemedicine Appointment Data Pipeline project.

## System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL
- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ recommended
- **Disk Space**: 10GB+ free space
- **Network**: Internet connection for package installation

## Software Prerequisites

- **Python**: Version 3.10 or higher
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: Version 2.30 or higher

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/telemedicine-pipeline.git
cd telemedicine-pipeline
```

### 2. Environment Setup

#### Option A: Using the Setup Script (Recommended)

The project includes a setup script that automates the installation process:

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Create necessary directories
- Install Python dependencies
- Set up Docker environment
- Configure local development tools

#### Option B: Manual Setup

If you prefer to set up the environment manually:

1. Create necessary directories:

```bash
mkdir -p data_sources/appointment_logs data_sources/patient_feedback data_sources/provider_data
mkdir -p data_ingestion/airflow/dags
mkdir -p data_processing/results
mkdir -p data_warehouse/schemas
mkdir -p visualization/dashboards
mkdir -p monitoring/logs monitoring/metrics monitoring/config
mkdir -p docs
```

2. Install Python dependencies:

```bash
pip3 install pandas numpy boto3 apache-airflow pyspark kafka-python sqlalchemy psycopg2-binary matplotlib seaborn dbt-core dbt-postgres
```

3. Set up Docker environment:

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
```

### 3. Configuration

1. Create a `.env` file with the following environment variables:

```bash
# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=telemedicine

# Redshift configuration
REDSHIFT_HOST=localhost
REDSHIFT_PORT=5439
REDSHIFT_USER=redshift
REDSHIFT_PASSWORD=redshift
REDSHIFT_DB=redshift

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_APPOINTMENTS=telemedicine-appointments
KAFKA_TOPIC_EVENTS=telemedicine-events

# Monitoring configuration
ALERT_EMAIL=admin@example.com
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=alerts@example.com
SMTP_PASSWORD=password
```

2. Configure Docker services by reviewing the `docker-compose.yml` file and making any necessary adjustments.

### 4. Start Services

Start the required services using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- Kafka and Zookeeper for streaming data
- PostgreSQL for provider data
- Airflow for workflow orchestration
- Redshift-compatible PostgreSQL for data warehouse

Verify that all services are running:

```bash
docker-compose ps
```

### 5. Generate Sample Data

Generate sample data for testing:

```bash
cd data_sources
python3 generate_data.py
```

This will create:
- Appointment logs
- Patient feedback data
- Provider and patient data

### 6. Run the Data Pipeline

Execute the data processing pipeline:

```bash
cd data_processing
python3 pipeline_orchestrator.py
```

This will:
1. Transform raw data into dimension and fact tables
2. Perform data quality checks
3. Generate a pipeline summary report

### 7. Build the Data Warehouse

Build the data warehouse structure:

```bash
cd data_warehouse/scripts
python3 build_warehouse_sqlite.py  # For local development
# or
python3 build_warehouse.py  # For Redshift deployment
```

### 8. Create Visualization Dashboard

Generate the visualization dashboard:

```bash
cd visualization/dashboards
python3 create_dashboard.py
```

Then open `dashboard.html` in a web browser to view the dashboard.

### 9. Set Up Monitoring

Set up the monitoring system:

```bash
cd monitoring/setup
chmod +x setup_monitoring.sh
./setup_monitoring.sh
```

This will:
- Configure alert thresholds
- Set up scheduled monitoring
- Create a monitoring dashboard

To view the monitoring dashboard:

```bash
cd monitoring/dashboard
python3 create_monitoring_dashboard.py
```

Then open `monitoring_dashboard.html` in a web browser.

## Troubleshooting

### Common Issues and Solutions

#### Docker Services Not Starting

If Docker services fail to start:

```bash
# Check Docker service status
sudo systemctl status docker

# Start Docker service if not running
sudo systemctl start docker

# Check Docker logs
sudo journalctl -xeu docker.service
```

#### Database Connection Issues

If you encounter database connection issues:

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify connection parameters in .env file
```

#### Kafka Connection Issues

If Kafka connection fails:

```bash
# Check if Kafka and Zookeeper are running
docker-compose ps kafka zookeeper

# Check Kafka logs
docker-compose logs kafka

# Verify Kafka topic creation
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

#### Python Dependency Issues

If you encounter Python dependency issues:

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies in the virtual environment
pip install -r requirements.txt
```

## Maintenance

### Backup and Restore

To backup the data warehouse:

```bash
# For SQLite
cp data_warehouse/telemedicine.db data_warehouse/telemedicine.db.backup

# For PostgreSQL
pg_dump -h localhost -p 5432 -U postgres -d telemedicine > telemedicine_backup.sql
```

To restore from backup:

```bash
# For SQLite
cp data_warehouse/telemedicine.db.backup data_warehouse/telemedicine.db

# For PostgreSQL
psql -h localhost -p 5432 -U postgres -d telemedicine < telemedicine_backup.sql
```

### Updating the Pipeline

To update the pipeline:

1. Pull the latest changes:

```bash
git pull origin main
```

2. Restart services:

```bash
docker-compose down
docker-compose up -d
```

3. Run the setup script to install any new dependencies:

```bash
./setup.sh
```

## Security Considerations

- The default credentials in the `.env` file are for development only. Change them for production use.
- Sensitive data should be encrypted at rest and in transit.
- Use proper authentication and authorization for all services.
- Regularly update dependencies to address security vulnerabilities.

## Next Steps

After successful installation:

1. Explore the visualization dashboard to understand the data.
2. Review the monitoring dashboard to ensure system health.
3. Customize alert thresholds in the monitoring configuration.
4. Integrate with your actual data sources by modifying the connectors.

For more information, refer to the main [README.md](README.md) file.
