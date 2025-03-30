# Telemedicine Appointment Data Pipeline

## Project Overview

This project implements a comprehensive data pipeline for telemedicine appointment data, designed to capture appointment logs, merge them with patient feedback, and provide operational insights to improve efficiency. The pipeline includes real-time data ingestion, scheduled ETL processes, dimensional data modeling, visualization dashboards, and monitoring systems.

## Architecture

The Telemedicine Appointment Data Pipeline consists of the following components:

1. **Data Sources**
   - Appointment logs from external APIs and streaming services
   - Patient feedback forms stored as JSON files
   - Provider and scheduling data from relational databases

2. **Data Ingestion**
   - Kafka for real-time appointment logs and events
   - Airflow for scheduled ingestion tasks
   - Custom connectors for external data sources

3. **Data Processing**
   - ETL scripts for data transformation
   - Dimensional modeling (star schema)
   - Data quality checks and validation

4. **Data Warehouse**
   - Redshift-compatible database structure
   - Fact and dimension tables
   - Data retention policies

5. **Visualization**
   - Interactive dashboards
   - Key performance metrics
   - Operational insights

6. **Monitoring & Alerts**
   - Real-time system monitoring
   - Configurable alert thresholds
   - Email and Slack notifications

## Directory Structure

```
telemedicine_pipeline/
├── data_sources/              # Simulated data sources
│   ├── appointment_logs/      # Appointment log data
│   ├── patient_feedback/      # Patient feedback data
│   ├── provider_data/         # Provider and patient data
│   └── generate_data.py       # Data generation script
├── data_ingestion/            # Data ingestion components
│   ├── airflow/               # Airflow DAGs and operators
│   ├── kafka/                 # Kafka producers and consumers
│   ├── external_api_connector.py  # External API connector
│   └── s3_feedback_connector.py   # S3 connector for feedback data
├── data_processing/           # Data processing pipeline
│   ├── etl/                   # ETL scripts
│   ├── results/               # Pipeline execution results
│   └── pipeline_orchestrator.py  # Pipeline orchestration
├── data_warehouse/            # Data warehouse components
│   ├── schemas/               # Database schema definitions
│   └── scripts/               # Data loading scripts
├── visualization/             # Visualization components
│   └── dashboards/            # Dashboard definitions and scripts
├── monitoring/                # Monitoring and alerts
│   ├── config/                # Alert configuration
│   ├── dashboard/             # Monitoring dashboard
│   ├── logs/                  # System logs
│   ├── metrics/               # Recorded metrics
│   ├── scripts/               # Monitoring scripts
│   └── setup/                 # Setup scripts
├── docs/                      # Project documentation
├── docker-compose.yml         # Docker services configuration
├── .env                       # Environment variables
├── setup.sh                   # Setup script
└── todo.md                    # Project task list
```

## Installation Guide

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Git

### Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/telemedicine-pipeline.git
cd telemedicine-pipeline
```

2. **Run the setup script**

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Create necessary directories
- Install Python dependencies
- Set up Docker environment
- Configure local development tools

3. **Start the services**

```bash
docker-compose up -d
```

This will start:
- Kafka and Zookeeper for streaming data
- PostgreSQL for provider data
- Airflow for workflow orchestration
- Redshift-compatible PostgreSQL for data warehouse

4. **Generate sample data**

```bash
cd data_sources
python3 generate_data.py
```

5. **Run the data pipeline**

```bash
cd data_processing
python3 pipeline_orchestrator.py
```

6. **Create visualization dashboard**

```bash
cd visualization/dashboards
python3 create_dashboard.py
```

7. **Set up monitoring**

```bash
cd monitoring/setup
./setup_monitoring.sh
```

## Usage Guide

### Data Ingestion

The data ingestion components can be used to ingest data from various sources:

1. **Kafka Streaming**

For real-time appointment logs:

```bash
cd data_ingestion/kafka
python3 appointment_producer.py  # Simulate appointment events
python3 appointment_consumer.py  # Process and store events
```

2. **Airflow DAGs**

The Airflow DAGs are scheduled to run automatically, but can also be triggered manually:

```bash
# Assuming Airflow is running
airflow dags trigger telemedicine_ingestion_dag
```

3. **External API Connector**

To fetch data from external APIs:

```bash
cd data_ingestion
python3 external_api_connector.py
```

### Data Processing

The data processing pipeline transforms raw data into a dimensional model:

```bash
cd data_processing
python3 pipeline_orchestrator.py
```

This will:
1. Transform raw data into dimension and fact tables
2. Perform data quality checks
3. Generate a pipeline summary report

### Data Warehouse

The data warehouse stores the transformed data in a dimensional model:

```bash
cd data_warehouse/scripts
python3 build_warehouse_sqlite.py  # For local development
# or
python3 build_warehouse.py  # For Redshift deployment
```

### Visualization Dashboard

To view the visualization dashboard:

```bash
cd visualization/dashboards
python3 create_dashboard.py
```

Then open `dashboard.html` in a web browser.

### Monitoring System

The monitoring system checks data quality, system performance, and business metrics:

```bash
cd monitoring/scripts
python3 monitoring_system.py
```

To view the monitoring dashboard:

```bash
cd monitoring/dashboard
python3 create_monitoring_dashboard.py
```

Then open `monitoring_dashboard.html` in a web browser.

## Data Model

The data warehouse uses a star schema with the following tables:

### Dimension Tables

1. **dim_date**
   - date_id (PK)
   - date
   - day, month, year, quarter
   - day_of_week, day_name, month_name
   - is_weekend, is_holiday

2. **dim_time**
   - time_id (PK)
   - time_value
   - hour, minute
   - am_pm, hour_12
   - day_period

3. **dim_provider**
   - provider_key (PK)
   - provider_id
   - first_name, last_name
   - specialty
   - years_experience
   - state
   - hourly_rate
   - available_hours
   - active

4. **dim_patient**
   - patient_key (PK)
   - patient_id
   - age, age_group
   - gender
   - has_insurance
   - registration_date

5. **dim_status**
   - status_key (PK)
   - status
   - is_successful

6. **dim_device**
   - device_key (PK)
   - device_type
   - is_mobile

### Fact Tables

1. **fact_appointment**
   - appointment_id (PK)
   - provider_key (FK)
   - patient_key (FK)
   - date_id (FK)
   - time_id (FK)
   - status_key (FK)
   - device_key (FK)
   - appointment_type
   - wait_time_minutes
   - duration_minutes
   - connection_quality
   - had_technical_issues
   - technical_issue_type
   - timestamp

2. **fact_feedback**
   - feedback_id (PK)
   - appointment_id (FK)
   - provider_key (FK)
   - patient_key (FK)
   - date_id (FK)
   - provider_rating
   - ease_of_use_rating
   - audio_quality_rating
   - video_quality_rating
   - overall_satisfaction
   - would_recommend
   - comments
   - timestamp

## Monitoring and Alerts

The monitoring system checks the following metrics:

1. **Data Freshness**
   - Time since last appointment
   - Time since last feedback

2. **Data Quality**
   - Null percentage in key columns
   - Minimum appointment count per day

3. **Business Metrics**
   - Appointment completion rate
   - Cancellation rate
   - No-show rate
   - Satisfaction ratings

4. **Technical Issues**
   - Technical issues percentage
   - Connection quality ratings

5. **System Performance**
   - Pipeline execution time
   - Query execution time

Alerts are sent via email or Slack when metrics exceed configured thresholds.

## Key Insights

The pipeline provides several key insights:

1. **Appointment Status Distribution**
   - Completed: 74.9%
   - Cancelled: 10.2%
   - Rescheduled: 10.1%
   - No-show: 4.9%

2. **Wait Times by Device**
   - Tablet: 14.17 minutes
   - Desktop: 14.04 minutes
   - Laptop: 13.91 minutes
   - Mobile Phone: 13.60 minutes

3. **Provider Ratings by Specialty**
   - Cardiology: 3.91 provider rating, 3.51 overall satisfaction
   - Internal Medicine: 3.61 provider rating, 3.42 overall satisfaction
   - Family Medicine: 3.77 provider rating, 3.35 overall satisfaction

4. **Technical Issues by Device**
   - Tablet: 17.04% of appointments
   - Mobile Phone: 16.90% of appointments
   - Desktop: 16.54% of appointments
   - Laptop: 16.33% of appointments

## Future Enhancements

Potential future enhancements for the pipeline include:

1. **Machine Learning Integration**
   - Predictive models for no-show risk
   - Appointment duration forecasting
   - Provider matching optimization

2. **Advanced Analytics**
   - Sentiment analysis on feedback comments
   - Patient journey mapping
   - Provider performance scoring

3. **Infrastructure Improvements**
   - Deployment to cloud services (AWS, Azure, GCP)
   - Containerization with Kubernetes
   - CI/CD pipeline integration

4. **User Interface**
   - Administrative portal for pipeline management
   - Custom dashboard builder
   - Mobile-optimized reporting

## Conclusion

The Telemedicine Appointment Data Pipeline provides a comprehensive solution for capturing, processing, and analyzing telemedicine appointment data. By merging appointment logs with patient feedback, the pipeline enables healthcare providers to identify operational inefficiencies, improve patient satisfaction, and optimize resource allocation.

The modular architecture allows for easy extension and customization, while the monitoring system ensures data quality and system reliability. The visualization dashboards provide actionable insights that can drive continuous improvement in telemedicine operations.
