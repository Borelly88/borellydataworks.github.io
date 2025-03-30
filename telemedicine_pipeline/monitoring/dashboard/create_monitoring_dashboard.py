import os
import json
import logging
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Configuration
DB_FILE = '/home/ubuntu/telemedicine_pipeline/data_warehouse/telemedicine.db'
LOG_DIR = '/home/ubuntu/telemedicine_pipeline/monitoring/logs'
METRICS_DIR = '/home/ubuntu/telemedicine_pipeline/monitoring/metrics'
DASHBOARD_DIR = '/home/ubuntu/telemedicine_pipeline/monitoring/dashboard'

# Create directories if they don't exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(METRICS_DIR, exist_ok=True)
os.makedirs(DASHBOARD_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'monitoring_dashboard.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('telemedicine_monitoring_dashboard')

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
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return pd.DataFrame()

def load_metrics():
    """Load all metrics from the metrics directory"""
    metrics = {}
    
    try:
        for filename in os.listdir(METRICS_DIR):
            if filename.endswith('.json'):
                metric_name = filename.replace('.json', '')
                file_path = os.path.join(METRICS_DIR, filename)
                
                with open(file_path, 'r') as f:
                    metric_data = json.load(f)
                
                metrics[metric_name] = metric_data
        
        return metrics
    except Exception as e:
        logger.error(f"Error loading metrics: {e}")
        return {}

def create_metric_chart(metric_name, metric_data, title=None, ylabel=None):
    """Create a chart for a metric"""
    try:
        if not metric_data:
            logger.warning(f"No data available for metric: {metric_name}")
            return None
        
        # Extract timestamps and values
        timestamps = [datetime.strptime(item['timestamp'], '%Y-%m-%d %H:%M:%S') for item in metric_data]
        values = [item['value'] for item in metric_data]
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': timestamps,
            'value': values
        })
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Create chart
        plt.figure(figsize=(10, 6))
        plt.plot(df['timestamp'], df['value'], marker='o', linestyle='-')
        
        # Set title and labels
        plt.title(title or f"{metric_name.replace('_', ' ').title()} Over Time", fontsize=16)
        plt.xlabel('Time', fontsize=12)
        plt.ylabel(ylabel or metric_name.replace('_', ' ').title(), fontsize=12)
        
        # Format x-axis
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save chart
        output_file = os.path.join(DASHBOARD_DIR, f"{metric_name}_chart.png")
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        logger.info(f"Created chart for metric {metric_name}: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error creating chart for metric {metric_name}: {e}")
        return None

def create_appointment_status_chart(conn):
    """Create a chart showing appointment status distribution over time"""
    try:
        # Get dates for the last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        query = """
        SELECT 
            d.date,
            s.status,
            COUNT(*) as appointment_count
        FROM fact_appointment a
        JOIN dim_date d ON a.date_id = d.date_id
        JOIN dim_status s ON a.status_key = s.status_key
        WHERE a.date_id >= ?
        GROUP BY d.date, s.status
        ORDER BY d.date, s.status
        """
        
        df = execute_query(conn, query, params=(thirty_days_ago,))
        
        if df.empty:
            logger.warning("No data available for appointment status chart")
            return None
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Pivot the data
        pivot_df = df.pivot(index='date', columns='status', values='appointment_count').fillna(0)
        
        # Create chart
        plt.figure(figsize=(12, 8))
        pivot_df.plot(kind='area', stacked=True, ax=plt.gca(), alpha=0.7)
        
        plt.title('Appointment Status Distribution Over Time', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Number of Appointments', fontsize=12)
        plt.legend(title='Status')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save chart
        output_file = os.path.join(DASHBOARD_DIR, "appointment_status_trend_chart.png")
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        logger.info(f"Created appointment status trend chart: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error creating appointment status trend chart: {e}")
        return None

def create_technical_issues_by_device_chart(conn):
    """Create a chart showing technical issues by device type over time"""
    try:
        # Get dates for the last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        query = """
        SELECT 
            d.date,
            dev.device_type,
            SUM(CASE WHEN a.had_technical_issues = 1 THEN 1 ELSE 0 END) as issues_count,
            COUNT(*) as total_count,
            (SUM(CASE WHEN a.had_technical_issues = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as issues_percentage
        FROM fact_appointment a
        JOIN dim_date d ON a.date_id = d.date_id
        JOIN dim_device dev ON a.device_key = dev.device_key
        WHERE a.date_id >= ?
        GROUP BY d.date, dev.device_type
        ORDER BY d.date, dev.device_type
        """
        
        df = execute_query(conn, query, params=(thirty_days_ago,))
        
        if df.empty:
            logger.warning("No data available for technical issues by device chart")
            return None
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Pivot the data
        pivot_df = df.pivot(index='date', columns='device_type', values='issues_percentage').fillna(0)
        
        # Create chart
        plt.figure(figsize=(12, 8))
        pivot_df.plot(kind='line', marker='o', ax=plt.gca())
        
        plt.title('Technical Issues by Device Type Over Time', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Percentage of Appointments with Issues', fontsize=12)
        plt.legend(title='Device Type')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save chart
        output_file = os.path.join(DASHBOARD_DIR, "technical_issues_by_device_trend_chart.png")
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        logger.info(f"Created technical issues by device trend chart: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error creating technical issues by device trend chart: {e}")
        return None

def create_satisfaction_by_specialty_chart(conn):
    """Create a chart showing satisfaction ratings by specialty"""
    try:
        # Get dates for the last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        query = """
        SELECT 
            p.specialty,
            AVG(f.provider_rating) as avg_provider_rating,
            AVG(f.overall_satisfaction) as avg_satisfaction
        FROM fact_feedback f
        JOIN dim_provider p ON f.provider_key = p.provider_key
        WHERE f.date_id >= ?
        GROUP BY p.specialty
        ORDER BY avg_satisfaction DESC
        """
        
        df = execute_query(conn, query, params=(thirty_days_ago,))
        
        if df.empty:
            logger.warning("No data available for satisfaction by specialty chart")
            return None
        
        # Create chart
        plt.figure(figsize=(12, 8))
        
        # Create a grouped bar chart
        x = range(len(df))
        width = 0.35
        
        plt.bar(x, df['avg_provider_rating'], width, label='Provider Rating')
        plt.bar([i + width for i in x], df['avg_satisfaction'], width, label='Overall Satisfaction')
        
        plt.xlabel('Specialty', fontsize=12)
        plt.ylabel('Average Rating (1-5)', fontsize=12)
        plt.title('Provider Ratings by Specialty (Last 30 Days)', fontsize=16)
        plt.xticks([i + width/2 for i in x], df['specialty'], rotation=45, ha='right')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save chart
        output_file = os.path.join(DASHBOARD_DIR, "satisfaction_by_specialty_chart.png")
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        logger.info(f"Created satisfaction by specialty chart: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error creating satisfaction by specialty chart: {e}")
        return None

def create_alerts_summary_chart():
    """Create a chart showing alerts summary"""
    try:
        # Get all alert files
        alert_files = [f for f in os.listdir(LOG_DIR) if f.startswith('alerts_') and f.endswith('.json')]
        
        if not alert_files:
            logger.warning("No alert files found")
            return None
        
        # Load all alerts
        all_alerts = []
        for file in alert_files:
            file_path = os.path.join(LOG_DIR, file)
            try:
                with open(file_path, 'r') as f:
                    alerts = json.load(f)
                    all_alerts.extend(alerts)
            except Exception as e:
                logger.error(f"Error loading alerts from {file_path}: {e}")
        
        if not all_alerts:
            logger.warning("No alerts found in files")
            return None
        
        # Count alerts by type and severity
        alert_counts = {}
        for alert in all_alerts:
            alert_type = alert.get('type', 'unknown')
            severity = alert.get('severity', 'unknown')
            
            if alert_type not in alert_counts:
                alert_counts[alert_type] = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'unknown': 0}
            
            alert_counts[alert_type][severity] += 1
        
        # Create DataFrame
        rows = []
        for alert_type, severities in alert_counts.items():
            for severity, count in severities.items():
                if count > 0:
                    rows.append({
                        'alert_type': alert_type,
                        'severity': severity,
                        'count': count
                    })
        
        df = pd.DataFrame(rows)
        
        if df.empty:
            logger.warning("No alerts data available for chart")
            return None
        
        # Create chart
        plt.figure(figsize=(12, 8))
        
        # Create a grouped bar chart
        chart = sns.barplot(x='alert_type', y='count', hue='severity', data=df)
        
        # Add value labels on top of bars
        for p in chart.patches:
            chart.annotate(format(p.get_height(), '.0f'),
                          (p.get_x() + p.get_width() / 2., p.get_height()),
                          ha = 'center', va = 'center',
                          xytext = (0, 9),
                          textcoords = 'offset points')
        
        plt.title('Alerts by Type and Severity', fontsize=16)
        plt.xlabel('Alert Type', fontsize=12)
        plt.ylabel('Number of Alerts', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save chart
        output_file = os.path.join(DASHBOARD_DIR, "alerts_summary_chart.png")
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        logger.info(f"Created alerts summary chart: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error creating alerts summary chart: {e}")
        return None

def create_monitoring_dashboard_html(charts):
    """Create an HTML dashboard with all monitoring charts"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Telemedicine Pipeline Monitoring Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .dashboard {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                border-radius: 5px 5px 0 0;
                margin-bottom: 20px;
            }
            .chart-container {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: center;
            }
            .chart {
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
                margin-bottom: 20px;
                width: calc(50% - 20px);
            }
            .chart img {
                width: 100%;
                height: auto;
            }
            .chart h3 {
                margin-top: 0;
                color: #2c3e50;
            }
            .footer {
                text-align: center;
                margin-top: 20px;
                color: #7f8c8d;
                font-size: 0.9em;
            }
            @media (max-width: 768px) {
                .chart {
                    width: 100%;
                }
            }
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="header">
                <h1>Telemedicine Pipeline Monitoring Dashboard</h1>
                <p>System health, metrics, and alerts for the Telemedicine Appointment Data Pipeline</p>
            </div>
            
            <div class="chart-container">
    """
    
    # Add each chart to the dashboard
    chart_titles = {
        'appointment_status_trend_chart.png': 'Appointment Status Distribution Over Time',
        'technical_issues_by_device_trend_chart.png': 'Technical Issues by Device Type Over Time',
        'satisfaction_by_specialty_chart.png': 'Provider Ratings by Specialty',
        'alerts_summary_chart.png': 'Alerts Summary by Type and Severity',
        'completion_rate_chart.png': 'Appointment Completion Rate Over Time',
        'cancellation_rate_chart.png': 'Appointment Cancellation Rate Over Time',
        'no_show_rate_chart.png': 'Appointment No-Show Rate Over Time',
        'avg_satisfaction_chart.png': 'Average Satisfaction Rating Over Time',
        'technical_issues_percentage_chart.png': 'Technical Issues Percentage Over Time',
        'avg_connection_quality_chart.png': 'Average Connection Quality Over Time',
        'pipeline_execution_time_minutes_chart.png': 'Pipeline Execution Time Over Time',
        'query_execution_time_chart.png': 'Query Execution Time Over Time'
    }
    
    for chart_file in charts:
        if chart_file:
            chart_name = os.path.basename(chart_file)
            title = chart_titles.get(chart_name, chart_name.replace('_chart.png', '').replace('_', ' ').title())
            
            html_content += f"""
                <div class="chart">
                    <h3>{title}</h3>
                    <img src="{os.path.basename(chart_file)}" alt="{title}">
                </div>
            """
    
    html_content += """
            </div>
            
            <div class="footer">
                <p>Generated on """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
                <p>Telemedicine Appointment Data Pipeline Monitoring System</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save the HTML file
    output_file = os.path.join(DASHBOARD_DIR, 'monitoring_dashboard.html')
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    logger.info(f"Created monitoring dashboard HTML: {output_file}")
    return output_file

def main():
    """Main function to create monitoring dashboard"""
    logger.info("Starting monitoring dashboard creation")
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        charts = []
        
        # Create database-based charts
        logger.info("Creating database-based charts")
        charts.append(create_appointment_status_chart(conn))
        charts.append(create_technical_issues_by_device_chart(conn))
        charts.append(create_satisfaction_by_specialty_chart(conn))
        
        # Create alerts summary chart
        logger.info("Creating alerts summary chart")
        charts.append(create_alerts_summary_chart())
        
        # Create metric charts
        logger.info("Creating metric charts")
        metrics = load_metrics()
        
        for metric_name, metric_data in metrics.items():
            # Customize chart titles and labels based on metric name
            title = None
            ylabel = None
            
            if metric_name == 'completion_rate':
                title = 'Appointment Completion Rate Over Time'
                ylabel = 'Completion Rate (%)'
            elif metric_name == 'cancellation_rate':
                title = 'Appointment Cancellation Rate Over Time'
                ylabel = 'Cancellation Rate (%)'
            elif metric_name == 'no_show_rate':
                title = 'Appointment No-Show Rate Over Time'
                ylabel = 'No-Show Rate (%)'
            elif metric_name == 'avg_satisfaction':
                title = 'Average Satisfaction Rating Over Time'
                ylabel = 'Satisfaction Rating (1-5)'
            elif metric_name == 'technical_issues_percentage':
                title = 'Technical Issues Percentage Over Time'
                ylabel = 'Issues Percentage (%)'
            elif metric_name == 'avg_connection_quality':
                title = 'Average Connection Quality Over Time'
                ylabel = 'Connection Quality Rating (1-5)'
            elif metric_name == 'pipeline_execution_time_minutes':
                title = 'Pipeline Execution Time Over Time'
                ylabel = 'Execution Time (minutes)'
            elif metric_name == 'query_execution_time':
                title = 'Query Execution Time Over Time'
                ylabel = 'Execution Time (seconds)'
            
            chart_file = create_metric_chart(metric_name, metric_data, title, ylabel)
            charts.append(chart_file)
        
        # Create dashboard HTML
        logger.info("Creating monitoring dashboard HTML")
        dashboard_html = create_monitoring_dashboard_html([c for c in charts if c])
        
        logger.info(f"Monitoring dashboard creation complete! Dashboard available at: {dashboard_html}")
        
    finally:
        # Close connection
        if conn:
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    main()
