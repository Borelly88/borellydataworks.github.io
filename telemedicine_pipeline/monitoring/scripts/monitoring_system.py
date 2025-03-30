import os
import json
import time
import sqlite3
import logging
import smtplib
import pandas as pd
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
DB_FILE = '/home/ubuntu/telemedicine_pipeline/data_warehouse/telemedicine.db'
LOG_DIR = '/home/ubuntu/telemedicine_pipeline/monitoring/logs'
ALERT_CONFIG_FILE = '/home/ubuntu/telemedicine_pipeline/monitoring/config/alert_config.json'
METRICS_DIR = '/home/ubuntu/telemedicine_pipeline/monitoring/metrics'

# Create directories if they don't exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(os.path.dirname(ALERT_CONFIG_FILE), exist_ok=True)
os.makedirs(METRICS_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'monitoring.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('telemedicine_monitoring')

# Default alert configuration
DEFAULT_ALERT_CONFIG = {
    "data_freshness": {
        "max_hours_since_last_appointment": 24,
        "max_hours_since_last_feedback": 48,
        "enabled": True,
        "severity": "HIGH"
    },
    "data_quality": {
        "max_null_percentage": 5.0,
        "min_appointment_count_per_day": 50,
        "enabled": True,
        "severity": "HIGH"
    },
    "system_performance": {
        "max_pipeline_execution_time_minutes": 30,
        "max_query_execution_time_seconds": 10,
        "enabled": True,
        "severity": "MEDIUM"
    },
    "business_metrics": {
        "min_completion_rate_percentage": 70.0,
        "max_cancellation_rate_percentage": 15.0,
        "max_no_show_rate_percentage": 10.0,
        "min_satisfaction_rating": 3.0,
        "enabled": True,
        "severity": "LOW"
    },
    "technical_issues": {
        "max_technical_issues_percentage": 20.0,
        "min_connection_quality_rating": 2.5,
        "enabled": True,
        "severity": "MEDIUM"
    },
    "notification": {
        "email": {
            "enabled": True,
            "recipients": ["admin@example.com", "operations@example.com"],
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "alerts@example.com",
            "smtp_password": "password"
        },
        "slack": {
            "enabled": False,
            "webhook_url": "https://hooks.slack.com/services/TXXXXXXXX/BXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX",
            "channel": "#telemedicine-alerts"
        }
    }
}

def create_default_alert_config():
    """Create default alert configuration file if it doesn't exist"""
    if not os.path.exists(ALERT_CONFIG_FILE):
        with open(ALERT_CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_ALERT_CONFIG, f, indent=4)
        logger.info(f"Created default alert configuration at {ALERT_CONFIG_FILE}")
    return DEFAULT_ALERT_CONFIG

def load_alert_config():
    """Load alert configuration from file"""
    try:
        if not os.path.exists(ALERT_CONFIG_FILE):
            return create_default_alert_config()
        
        with open(ALERT_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded alert configuration from {ALERT_CONFIG_FILE}")
        return config
    except Exception as e:
        logger.error(f"Error loading alert configuration: {e}")
        return DEFAULT_ALERT_CONFIG

def connect_to_database():
    """Connect to the SQLite database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        logger.info(f"Connected to database: {DB_FILE}")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def execute_query(conn, query, params=None):
    """Execute a query and return the results as a DataFrame"""
    try:
        start_time = time.time()
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        
        execution_time = time.time() - start_time
        logger.debug(f"Query executed in {execution_time:.2f} seconds")
        
        # Record query performance
        record_metric("query_execution_time", execution_time)
        
        return df, execution_time
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return pd.DataFrame(), 0

def check_data_freshness(conn, config):
    """Check if data is being updated regularly"""
    alerts = []
    
    if not config["data_freshness"]["enabled"]:
        return alerts
    
    # Check last appointment timestamp
    query = """
    SELECT MAX(timestamp) as last_appointment_time
    FROM fact_appointment
    """
    df, _ = execute_query(conn, query)
    
    if not df.empty and df['last_appointment_time'].iloc[0] is not None:
        last_appointment_time = pd.to_datetime(df['last_appointment_time'].iloc[0])
        hours_since_last_appointment = (datetime.now() - last_appointment_time).total_seconds() / 3600
        
        if hours_since_last_appointment > config["data_freshness"]["max_hours_since_last_appointment"]:
            alert = {
                "type": "data_freshness",
                "severity": config["data_freshness"]["severity"],
                "message": f"No new appointments in the last {hours_since_last_appointment:.1f} hours (threshold: {config['data_freshness']['max_hours_since_last_appointment']} hours)",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            alerts.append(alert)
            logger.warning(alert["message"])
    
    # Check last feedback timestamp
    query = """
    SELECT MAX(timestamp) as last_feedback_time
    FROM fact_feedback
    """
    df, _ = execute_query(conn, query)
    
    if not df.empty and df['last_feedback_time'].iloc[0] is not None:
        last_feedback_time = pd.to_datetime(df['last_feedback_time'].iloc[0])
        hours_since_last_feedback = (datetime.now() - last_feedback_time).total_seconds() / 3600
        
        if hours_since_last_feedback > config["data_freshness"]["max_hours_since_last_feedback"]:
            alert = {
                "type": "data_freshness",
                "severity": config["data_freshness"]["severity"],
                "message": f"No new feedback in the last {hours_since_last_feedback:.1f} hours (threshold: {config['data_freshness']['max_hours_since_last_feedback']} hours)",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            alerts.append(alert)
            logger.warning(alert["message"])
    
    return alerts

def check_data_quality(conn, config):
    """Check data quality metrics"""
    alerts = []
    
    if not config["data_quality"]["enabled"]:
        return alerts
    
    # Check for null values in important columns
    query = """
    SELECT 
        SUM(CASE WHEN provider_key IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as provider_null_pct,
        SUM(CASE WHEN patient_key IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as patient_null_pct,
        SUM(CASE WHEN date_id IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as date_null_pct,
        SUM(CASE WHEN time_id IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as time_null_pct,
        COUNT(*) as total_count
    FROM fact_appointment
    """
    df, _ = execute_query(conn, query)
    
    if not df.empty:
        for column in ['provider_null_pct', 'patient_null_pct', 'date_null_pct', 'time_null_pct']:
            null_pct = df[column].iloc[0]
            if null_pct > config["data_quality"]["max_null_percentage"]:
                column_name = column.replace('_null_pct', '')
                alert = {
                    "type": "data_quality",
                    "severity": config["data_quality"]["severity"],
                    "message": f"High percentage of NULL values in {column_name} column: {null_pct:.1f}% (threshold: {config['data_quality']['max_null_percentage']}%)",
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                alerts.append(alert)
                logger.warning(alert["message"])
    
    # Check appointment count per day for the last 7 days
    query = """
    SELECT date_id, COUNT(*) as appointment_count
    FROM fact_appointment
    WHERE date_id >= ?
    GROUP BY date_id
    """
    
    # Get date 7 days ago in YYYYMMDD format
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
    
    df, _ = execute_query(conn, query, params=(seven_days_ago,))
    
    if not df.empty:
        for _, row in df.iterrows():
            if row['appointment_count'] < config["data_quality"]["min_appointment_count_per_day"]:
                alert = {
                    "type": "data_quality",
                    "severity": config["data_quality"]["severity"],
                    "message": f"Low appointment count on {row['date_id']}: {row['appointment_count']} appointments (threshold: {config['data_quality']['min_appointment_count_per_day']})",
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                alerts.append(alert)
                logger.warning(alert["message"])
    
    return alerts

def check_business_metrics(conn, config):
    """Check business metrics"""
    alerts = []
    
    if not config["business_metrics"]["enabled"]:
        return alerts
    
    # Check appointment completion rate
    query = """
    SELECT 
        SUM(CASE WHEN s.status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as completion_rate,
        SUM(CASE WHEN s.status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as cancellation_rate,
        SUM(CASE WHEN s.status = 'No-show' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as no_show_rate,
        COUNT(*) as total_count
    FROM fact_appointment a
    JOIN dim_status s ON a.status_key = s.status_key
    WHERE a.date_id >= ?
    """
    
    # Get date 30 days ago in YYYYMMDD format
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    
    df, _ = execute_query(conn, query, params=(thirty_days_ago,))
    
    if not df.empty:
        completion_rate = df['completion_rate'].iloc[0]
        cancellation_rate = df['cancellation_rate'].iloc[0]
        no_show_rate = df['no_show_rate'].iloc[0]
        
        # Record business metrics
        record_metric("completion_rate", completion_rate)
        record_metric("cancellation_rate", cancellation_rate)
        record_metric("no_show_rate", no_show_rate)
        
        if completion_rate < config["business_metrics"]["min_completion_rate_percentage"]:
            alert = {
                "type": "business_metrics",
                "severity": config["business_metrics"]["severity"],
                "message": f"Low appointment completion rate: {completion_rate:.1f}% (threshold: {config['business_metrics']['min_completion_rate_percentage']}%)",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            alerts.append(alert)
            logger.warning(alert["message"])
        
        if cancellation_rate > config["business_metrics"]["max_cancellation_rate_percentage"]:
            alert = {
                "type": "business_metrics",
                "severity": config["business_metrics"]["severity"],
                "message": f"High appointment cancellation rate: {cancellation_rate:.1f}% (threshold: {config['business_metrics']['max_cancellation_rate_percentage']}%)",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            alerts.append(alert)
            logger.warning(alert["message"])
        
        if no_show_rate > config["business_metrics"]["max_no_show_rate_percentage"]:
            alert = {
                "type": "business_metrics",
                "severity": config["business_metrics"]["severity"],
                "message": f"High appointment no-show rate: {no_show_rate:.1f}% (threshold: {config['business_metrics']['max_no_show_rate_percentage']}%)",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            alerts.append(alert)
            logger.warning(alert["message"])
    
    # Check satisfaction ratings
    query = """
    SELECT AVG(overall_satisfaction) as avg_satisfaction
    FROM fact_feedback
    WHERE date_id >= ?
    """
    
    df, _ = execute_query(conn, query, params=(thirty_days_ago,))
    
    if not df.empty and df['avg_satisfaction'].iloc[0] is not None:
        avg_satisfaction = df['avg_satisfaction'].iloc[0]
        
        # Record satisfaction metric
        record_metric("avg_satisfaction", avg_satisfaction)
        
        if avg_satisfaction < config["business_metrics"]["min_satisfaction_rating"]:
            alert = {
                "type": "business_metrics",
                "severity": config["business_metrics"]["severity"],
                "message": f"Low overall satisfaction rating: {avg_satisfaction:.1f} (threshold: {config['business_metrics']['min_satisfaction_rating']})",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            alerts.append(alert)
            logger.warning(alert["message"])
    
    return alerts

def check_technical_issues(conn, config):
    """Check technical issues metrics"""
    alerts = []
    
    if not config["technical_issues"]["enabled"]:
        return alerts
    
    # Check technical issues percentage
    query = """
    SELECT 
        SUM(CASE WHEN had_technical_issues = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as issues_percentage,
        COUNT(*) as total_count
    FROM fact_appointment
    WHERE date_id >= ?
    """
    
    # Get date 30 days ago in YYYYMMDD format
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    
    df, _ = execute_query(conn, query, params=(thirty_days_ago,))
    
    if not df.empty:
        issues_percentage = df['issues_percentage'].iloc[0]
        
        # Record technical issues metric
        record_metric("technical_issues_percentage", issues_percentage)
        
        if issues_percentage > config["technical_issues"]["max_technical_issues_percentage"]:
            alert = {
                "type": "technical_issues",
                "severity": config["technical_issues"]["severity"],
                "message": f"High percentage of technical issues: {issues_percentage:.1f}% (threshold: {config['technical_issues']['max_technical_issues_percentage']}%)",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            alerts.append(alert)
            logger.warning(alert["message"])
    
    # Check connection quality
    query = """
    SELECT AVG(CAST(CASE 
                WHEN connection_quality = 'Excellent' THEN 5
                WHEN connection_quality = 'Good' THEN 4
                WHEN connection_quality = 'Fair' THEN 3
                WHEN connection_quality = 'Poor' THEN 2
                WHEN connection_quality = 'Very Poor' THEN 1
                ELSE NULL
            END AS FLOAT)) as avg_connection_quality
    FROM fact_appointment
    WHERE date_id >= ?
    """
    
    df, _ = execute_query(conn, query, params=(thirty_days_ago,))
    
    if not df.empty and df['avg_connection_quality'].iloc[0] is not None:
        avg_connection_quality = df['avg_connection_quality'].iloc[0]
        
        # Record connection quality metric
        record_metric("avg_connection_quality", avg_connection_quality)
        
        if avg_connection_quality < config["technical_issues"]["min_connection_quality_rating"]:
            alert = {
                "type": "technical_issues",
                "severity": config["technical_issues"]["severity"],
                "message": f"Low average connection quality: {avg_connection_quality:.1f} (threshold: {config['technical_issues']['min_connection_quality_rating']})",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            alerts.append(alert)
            logger.warning(alert["message"])
    
    return alerts

def check_system_performance(config, pipeline_execution_time=None):
    """Check system performance metrics"""
    alerts = []
    
    if not config["system_performance"]["enabled"]:
        return alerts
    
    # Check pipeline execution time if provided
    if pipeline_execution_time is not None:
        pipeline_execution_time_minutes = pipeline_execution_time / 60.0
        
        # Record pipeline execution time
        record_metric("pipeline_execution_time_minutes", pipeline_execution_time_minutes)
        
        if pipeline_execution_time_minutes > config["system_performance"]["max_pipeline_execution_time_minutes"]:
            alert = {
                "type": "system_performance",
                "severity": config["system_performance"]["severity"],
                "message": f"Long pipeline execution time: {pipeline_execution_time_minutes:.1f} minutes (threshold: {config['system_performance']['max_pipeline_execution_time_minutes']} minutes)",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            alerts.append(alert)
            logger.warning(alert["message"])
    
    # Check query execution times from metrics
    query_times = get_metric_history("query_execution_time")
    if query_times:
        max_query_time = max(query_times)
        if max_query_time > config["system_performance"]["max_query_execution_time_seconds"]:
            alert = {
                "type": "system_performance",
                "severity": config["system_performance"]["severity"],
                "message": f"Long query execution time: {max_query_time:.1f} seconds (threshold: {config['system_performance']['max_query_execution_time_seconds']} seconds)",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            alerts.append(alert)
            logger.warning(alert["message"])
    
    return alerts

def record_metric(metric_name, value):
    """Record a metric value with timestamp"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create metric file if it doesn't exist
        metric_file = os.path.join(METRICS_DIR, f"{metric_name}.json")
        
        if os.path.exists(metric_file):
            with open(metric_file, 'r') as f:
                metrics = json.load(f)
        else:
            metrics = []
        
        # Add new metric
        metrics.append({
            "timestamp": timestamp,
            "value": value
        })
        
        # Keep only the last 100 metrics
        if len(metrics) > 100:
            metrics = metrics[-100:]
        
        # Save metrics
        with open(metric_file, 'w') as f:
            json.dump(metrics, f, indent=4)
        
        logger.debug(f"Recorded metric {metric_name}: {value}")
    except Exception as e:
        logger.error(f"Error recording metric {metric_name}: {e}")

def get_metric_history(metric_name):
    """Get historical values for a metric"""
    try:
        metric_file = os.path.join(METRICS_DIR, f"{metric_name}.json")
        
        if not os.path.exists(metric_file):
            return []
        
        with open(metric_file, 'r') as f:
            metrics = json.load(f)
        
        return [m["value"] for m in metrics]
    except Exception as e:
        logger.error(f"Error getting metric history for {metric_name}: {e}")
        return []

def send_email_alert(alert, config):
    """Send an email alert"""
    try:
        if not config["notification"]["email"]["enabled"]:
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = config["notification"]["email"]["smtp_username"]
        msg['To'] = ", ".join(config["notification"]["email"]["recipients"])
        msg['Subject'] = f"Telemedicine Pipeline Alert: {alert['type']} - {alert['severity']}"
        
        # Create message body
        body = f"""
        <html>
        <body>
            <h2>Telemedicine Pipeline Alert</h2>
            <p><strong>Type:</strong> {alert['type']}</p>
            <p><strong>Severity:</strong> {alert['severity']}</p>
            <p><strong>Message:</strong> {alert['message']}</p>
            <p><strong>Timestamp:</strong> {alert['timestamp']}</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to SMTP server
        server = smtplib.SMTP(
            config["notification"]["email"]["smtp_server"],
            config["notification"]["email"]["smtp_port"]
        )
        server.starttls()
        server.login(
            config["notification"]["email"]["smtp_username"],
            config["notification"]["email"]["smtp_password"]
        )
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Sent email alert: {alert['message']}")
        return True
    except Exception as e:
        logger.error(f"Error sending email alert: {e}")
        return False

def send_slack_alert(alert, config):
    """Send a Slack alert"""
    try:
        if not config["notification"]["slack"]["enabled"]:
            return False
        
        # This is a simplified version - in a real implementation, you would use
        # the Slack API or a webhook to send the message
        logger.info(f"Would send Slack alert to {config['notification']['slack']['channel']}: {alert['message']}")
        return True
    except Exception as e:
        logger.error(f"Error sending Slack alert: {e}")
        return False

def send_alert(alert, config):
    """Send an alert through configured channels"""
    email_sent = send_email_alert(alert, config)
    slack_sent = send_slack_alert(alert, config)
    
    return email_sent or slack_sent

def run_monitoring_checks(pipeline_execution_time=None):
    """Run all monitoring checks"""
    start_time = time.time()
    logger.info("Starting monitoring checks")
    
    # Load alert configuration
    config = load_alert_config()
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        all_alerts = []
        
        # Run checks
        data_freshness_alerts = check_data_freshness(conn, config)
        all_alerts.extend(data_freshness_alerts)
        
        data_quality_alerts = check_data_quality(conn, config)
        all_alerts.extend(data_quality_alerts)
        
        business_metrics_alerts = check_business_metrics(conn, config)
        all_alerts.extend(business_metrics_alerts)
        
        technical_issues_alerts = check_technical_issues(conn, config)
        all_alerts.extend(technical_issues_alerts)
        
        system_performance_alerts = check_system_performance(config, pipeline_execution_time)
        all_alerts.extend(system_performance_alerts)
        
        # Send alerts
        for alert in all_alerts:
            send_alert(alert, config)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        logger.info(f"Monitoring checks completed in {execution_time:.2f} seconds")
        logger.info(f"Found {len(all_alerts)} alerts")
        
        # Save alerts to file
        if all_alerts:
            alerts_file = os.path.join(LOG_DIR, f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(alerts_file, 'w') as f:
                json.dump(all_alerts, f, indent=4)
            logger.info(f"Saved alerts to {alerts_file}")
        
        return all_alerts
    finally:
        # Close connection
        if conn:
            conn.close()
            logger.info("Database connection closed")

def main():
    """Main function"""
    logger.info("Starting telemedicine pipeline monitoring system")
    
    # Run monitoring checks
    alerts = run_monitoring_checks()
    
    logger.info("Telemedicine pipeline monitoring system completed")
    return alerts

if __name__ == "__main__":
    main()
