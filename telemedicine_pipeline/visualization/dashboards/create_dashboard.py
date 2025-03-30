import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Set style for plots
plt.style.use('ggplot')
sns.set_palette("Set2")

# Database connection
DB_FILE = '/home/ubuntu/telemedicine_pipeline/data_warehouse/telemedicine.db'
OUTPUT_DIR = '/home/ubuntu/telemedicine_pipeline/visualization/dashboards'

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def connect_to_database():
    """Connect to the SQLite database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        print(f"Connected to database: {DB_FILE}")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_query(conn, query):
    """Execute a query and return the results as a DataFrame"""
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error executing query: {e}")
        return pd.DataFrame()

def create_appointment_status_chart(conn):
    """Create a chart showing appointment counts by status"""
    query = """
    SELECT s.status, COUNT(*) as appointment_count
    FROM fact_appointment a
    JOIN dim_status s ON a.status_key = s.status_key
    GROUP BY s.status
    ORDER BY appointment_count DESC
    """
    
    df = execute_query(conn, query)
    
    if df.empty:
        print("No data available for appointment status chart")
        return
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x='status', y='appointment_count', data=df)
    
    # Add value labels on top of bars
    for i, v in enumerate(df['appointment_count']):
        ax.text(i, v + 30, str(v), ha='center')
    
    plt.title('Appointment Counts by Status', fontsize=16)
    plt.xlabel('Status', fontsize=12)
    plt.ylabel('Number of Appointments', fontsize=12)
    plt.tight_layout()
    
    # Save the chart
    output_file = os.path.join(OUTPUT_DIR, 'appointment_status_chart.png')
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    print(f"Created appointment status chart: {output_file}")
    return output_file

def create_wait_time_chart(conn):
    """Create a chart showing average wait times by device type"""
    query = """
    SELECT d.device_type, AVG(a.wait_time_minutes) as avg_wait_time
    FROM fact_appointment a
    JOIN dim_device d ON a.device_key = d.device_key
    WHERE a.wait_time_minutes IS NOT NULL
    GROUP BY d.device_type
    ORDER BY avg_wait_time DESC
    """
    
    df = execute_query(conn, query)
    
    if df.empty:
        print("No data available for wait time chart")
        return
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x='device_type', y='avg_wait_time', data=df)
    
    # Add value labels on top of bars
    for i, v in enumerate(df['avg_wait_time']):
        ax.text(i, v + 0.3, f"{v:.2f}", ha='center')
    
    plt.title('Average Wait Time by Device Type', fontsize=16)
    plt.xlabel('Device Type', fontsize=12)
    plt.ylabel('Average Wait Time (minutes)', fontsize=12)
    plt.tight_layout()
    
    # Save the chart
    output_file = os.path.join(OUTPUT_DIR, 'wait_time_chart.png')
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    print(f"Created wait time chart: {output_file}")
    return output_file

def create_provider_rating_chart(conn):
    """Create a chart showing average provider ratings by specialty"""
    query = """
    SELECT p.specialty, 
           AVG(f.provider_rating) as avg_provider_rating,
           AVG(f.overall_satisfaction) as avg_satisfaction
    FROM fact_feedback f
    JOIN dim_provider p ON f.provider_key = p.provider_key
    GROUP BY p.specialty
    ORDER BY avg_satisfaction DESC
    """
    
    df = execute_query(conn, query)
    
    if df.empty:
        print("No data available for provider rating chart")
        return
    
    plt.figure(figsize=(12, 8))
    
    # Create a grouped bar chart
    x = range(len(df))
    width = 0.35
    
    plt.bar(x, df['avg_provider_rating'], width, label='Provider Rating')
    plt.bar([i + width for i in x], df['avg_satisfaction'], width, label='Overall Satisfaction')
    
    plt.xlabel('Specialty', fontsize=12)
    plt.ylabel('Average Rating (1-5)', fontsize=12)
    plt.title('Provider Ratings by Specialty', fontsize=16)
    plt.xticks([i + width/2 for i in x], df['specialty'], rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    
    # Save the chart
    output_file = os.path.join(OUTPUT_DIR, 'provider_rating_chart.png')
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    print(f"Created provider rating chart: {output_file}")
    return output_file

def create_technical_issues_chart(conn):
    """Create a chart showing technical issues by device type"""
    query = """
    SELECT d.device_type, 
           COUNT(*) as total_appointments,
           SUM(CASE WHEN a.had_technical_issues = 1 THEN 1 ELSE 0 END) as issues_count,
           (SUM(CASE WHEN a.had_technical_issues = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as issues_percentage
    FROM fact_appointment a
    JOIN dim_device d ON a.device_key = d.device_key
    GROUP BY d.device_type
    ORDER BY issues_percentage DESC
    """
    
    df = execute_query(conn, query)
    
    if df.empty:
        print("No data available for technical issues chart")
        return
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x='device_type', y='issues_percentage', data=df)
    
    # Add value labels on top of bars
    for i, v in enumerate(df['issues_percentage']):
        ax.text(i, v + 0.5, f"{v:.2f}%", ha='center')
    
    plt.title('Technical Issues by Device Type', fontsize=16)
    plt.xlabel('Device Type', fontsize=12)
    plt.ylabel('Percentage of Appointments with Issues', fontsize=12)
    plt.tight_layout()
    
    # Save the chart
    output_file = os.path.join(OUTPUT_DIR, 'technical_issues_chart.png')
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    print(f"Created technical issues chart: {output_file}")
    return output_file

def create_appointment_duration_chart(conn):
    """Create a chart showing average appointment duration by appointment type"""
    query = """
    SELECT appointment_type, AVG(duration_minutes) as avg_duration
    FROM fact_appointment
    WHERE duration_minutes IS NOT NULL
    GROUP BY appointment_type
    ORDER BY avg_duration DESC
    """
    
    df = execute_query(conn, query)
    
    if df.empty:
        print("No data available for appointment duration chart")
        return
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x='appointment_type', y='avg_duration', data=df)
    
    # Add value labels on top of bars
    for i, v in enumerate(df['avg_duration']):
        ax.text(i, v + 1, f"{v:.2f}", ha='center')
    
    plt.title('Average Appointment Duration by Type', fontsize=16)
    plt.xlabel('Appointment Type', fontsize=12)
    plt.ylabel('Average Duration (minutes)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save the chart
    output_file = os.path.join(OUTPUT_DIR, 'appointment_duration_chart.png')
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    print(f"Created appointment duration chart: {output_file}")
    return output_file

def create_patient_age_distribution_chart(conn):
    """Create a chart showing patient age distribution"""
    query = """
    SELECT age_group, COUNT(*) as patient_count
    FROM dim_patient
    GROUP BY age_group
    ORDER BY 
        CASE 
            WHEN age_group = 'Under 18' THEN 1
            WHEN age_group = '18-34' THEN 2
            WHEN age_group = '35-49' THEN 3
            WHEN age_group = '50-64' THEN 4
            WHEN age_group = '65+' THEN 5
        END
    """
    
    df = execute_query(conn, query)
    
    if df.empty:
        print("No data available for patient age distribution chart")
        return
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x='age_group', y='patient_count', data=df)
    
    # Add value labels on top of bars
    for i, v in enumerate(df['patient_count']):
        ax.text(i, v + 5, str(v), ha='center')
    
    plt.title('Patient Age Distribution', fontsize=16)
    plt.xlabel('Age Group', fontsize=12)
    plt.ylabel('Number of Patients', fontsize=12)
    plt.tight_layout()
    
    # Save the chart
    output_file = os.path.join(OUTPUT_DIR, 'patient_age_distribution_chart.png')
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    print(f"Created patient age distribution chart: {output_file}")
    return output_file

def create_dashboard_html(chart_files):
    """Create an HTML dashboard with all charts"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Telemedicine Appointment Dashboard</title>
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
                <h1>Telemedicine Appointment Dashboard</h1>
                <p>Key metrics and insights from telemedicine appointment data</p>
            </div>
            
            <div class="chart-container">
    """
    
    # Add each chart to the dashboard
    chart_titles = {
        'appointment_status_chart.png': 'Appointment Status Distribution',
        'wait_time_chart.png': 'Average Wait Time by Device Type',
        'provider_rating_chart.png': 'Provider Ratings by Specialty',
        'technical_issues_chart.png': 'Technical Issues by Device Type',
        'appointment_duration_chart.png': 'Average Appointment Duration by Type',
        'patient_age_distribution_chart.png': 'Patient Age Distribution'
    }
    
    for chart_file in chart_files:
        if chart_file:
            chart_name = os.path.basename(chart_file)
            title = chart_titles.get(chart_name, chart_name)
            
            html_content += f"""
                <div class="chart">
                    <h3>{title}</h3>
                    <img src="{chart_name}" alt="{title}">
                </div>
            """
    
    html_content += """
            </div>
            
            <div class="footer">
                <p>Generated on """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
                <p>Telemedicine Appointment Data Pipeline</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save the HTML file
    output_file = os.path.join(OUTPUT_DIR, 'dashboard.html')
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Created dashboard HTML: {output_file}")
    return output_file

def main():
    """Main function to create visualization dashboard"""
    print("Starting visualization dashboard creation...")
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Create charts
        chart_files = []
        
        print("\nCreating appointment status chart...")
        chart_files.append(create_appointment_status_chart(conn))
        
        print("\nCreating wait time chart...")
        chart_files.append(create_wait_time_chart(conn))
        
        print("\nCreating provider rating chart...")
        chart_files.append(create_provider_rating_chart(conn))
        
        print("\nCreating technical issues chart...")
        chart_files.append(create_technical_issues_chart(conn))
        
        print("\nCreating appointment duration chart...")
        chart_files.append(create_appointment_duration_chart(conn))
        
        print("\nCreating patient age distribution chart...")
        chart_files.append(create_patient_age_distribution_chart(conn))
        
        # Create dashboard HTML
        print("\nCreating dashboard HTML...")
        dashboard_html = create_dashboard_html(chart_files)
        
        print(f"\nDashboard creation complete! Dashboard available at: {dashboard_html}")
        
    finally:
        # Close connection
        if conn:
            conn.close()
            print("Database connection closed")

if __name__ == "__main__":
    main()
