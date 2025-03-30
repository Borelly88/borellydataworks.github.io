import os
import pandas as pd
import sqlite3
import time
from datetime import datetime

# Paths
TRANSFORMED_DATA_DIR = '/home/ubuntu/telemedicine_pipeline/data_processing/transformed'
SCHEMA_FILE = '/home/ubuntu/telemedicine_pipeline/data_warehouse/schemas/telemedicine_schema_sqlite.sql'
DB_FILE = '/home/ubuntu/telemedicine_pipeline/data_warehouse/telemedicine.db'

def create_sqlite_schema():
    """Create a SQLite version of the Redshift schema"""
    # Read the original Redshift schema
    with open('/home/ubuntu/telemedicine_pipeline/data_warehouse/schemas/telemedicine_schema.sql', 'r') as f:
        redshift_schema = f.read()
    
    # Convert Redshift-specific syntax to SQLite
    sqlite_schema = redshift_schema
    
    # Remove DISTSTYLE, DISTKEY, SORTKEY
    sqlite_schema = sqlite_schema.replace('DISTSTYLE ALL', '')
    sqlite_schema = sqlite_schema.replace('DISTKEY(date_id)', '')
    sqlite_schema = sqlite_schema.replace('SORTKEY(date_id)', '')
    sqlite_schema = sqlite_schema.replace('SORTKEY(date_id, time_id)', '')
    
    # Write the SQLite schema
    with open(SCHEMA_FILE, 'w') as f:
        f.write(sqlite_schema)
    
    print(f"Created SQLite schema at {SCHEMA_FILE}")
    return True

def connect_to_database():
    """Connect to the SQLite database"""
    try:
        # Remove existing database file if it exists
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            print(f"Removed existing database file: {DB_FILE}")
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        print(f"Connected to database: {DB_FILE}")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_schema_file(conn):
    """Execute the schema SQL file to create tables"""
    try:
        with open(SCHEMA_FILE, 'r') as f:
            schema_sql = f.read()
        
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        cursor.close()
        
        print("Schema created successfully")
        return True
    except Exception as e:
        print(f"Error creating schema: {e}")
        return False

def load_dimension_table(conn, table_name, file_name):
    """Load data into a dimension table from a CSV file"""
    try:
        # Read CSV file
        file_path = os.path.join(TRANSFORMED_DATA_DIR, file_name)
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} rows from {file_path}")
        
        # Insert data into SQLite
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        print(f"Loaded {len(df)} rows into {table_name}")
        return True
    except Exception as e:
        print(f"Error loading {table_name}: {e}")
        return False

def load_fact_table(conn, table_name, file_name):
    """Load data into a fact table from a CSV file"""
    try:
        # Read CSV file
        file_path = os.path.join(TRANSFORMED_DATA_DIR, file_name)
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} rows from {file_path}")
        
        # Insert data into SQLite
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        print(f"Loaded {len(df)} rows into {table_name}")
        return True
    except Exception as e:
        print(f"Error loading {table_name}: {e}")
        return False

def verify_data_loading(conn):
    """Verify that data was loaded correctly by counting rows in each table"""
    try:
        cursor = conn.cursor()
        
        tables = [
            'dim_date', 'dim_time', 'dim_provider', 'dim_patient', 
            'dim_status', 'dim_device', 'fact_appointment', 'fact_feedback'
        ]
        
        results = {}
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            results[table] = count
            print(f"Table {table}: {count} rows")
        
        cursor.close()
        return results
    except Exception as e:
        print(f"Error verifying data loading: {e}")
        return {}

def configure_data_retention(conn):
    """Configure data retention policies"""
    try:
        cursor = conn.cursor()
        
        # Create a table to track data retention policies
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_retention_policies (
            table_name VARCHAR(100) PRIMARY KEY,
            retention_period_days INTEGER NOT NULL,
            last_cleanup_date DATE NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Insert retention policies
        policies = [
            ('fact_appointment', 730),  # 2 years
            ('fact_feedback', 730),     # 2 years
            ('dim_date', 3650),         # 10 years
            ('dim_time', 3650),         # 10 years
            ('dim_provider', 1825),     # 5 years
            ('dim_patient', 1825),      # 5 years
            ('dim_status', 3650),       # 10 years
            ('dim_device', 3650)        # 10 years
        ]
        
        for table, days in policies:
            cursor.execute("""
            INSERT OR REPLACE INTO data_retention_policies 
            (table_name, retention_period_days, last_cleanup_date)
            VALUES (?, ?, date('now'))
            """, (table, days))
        
        conn.commit()
        cursor.close()
        print("Data retention policies configured")
        return True
    except Exception as e:
        print(f"Error configuring data retention policies: {e}")
        return False

def run_sample_queries(conn):
    """Run some sample queries to demonstrate the data warehouse"""
    try:
        cursor = conn.cursor()
        
        print("\nRunning sample queries...")
        
        # Query 1: Appointment counts by status
        print("\nQuery 1: Appointment counts by status")
        cursor.execute("""
        SELECT s.status, COUNT(*) as appointment_count
        FROM fact_appointment a
        JOIN dim_status s ON a.status_key = s.status_key
        GROUP BY s.status
        ORDER BY appointment_count DESC
        """)
        
        results = cursor.fetchall()
        for row in results:
            print(f"{row[0]}: {row[1]} appointments")
        
        # Query 2: Average wait time by device type
        print("\nQuery 2: Average wait time by device type")
        cursor.execute("""
        SELECT d.device_type, AVG(a.wait_time_minutes) as avg_wait_time
        FROM fact_appointment a
        JOIN dim_device d ON a.device_key = d.device_key
        GROUP BY d.device_type
        ORDER BY avg_wait_time DESC
        """)
        
        results = cursor.fetchall()
        for row in results:
            print(f"{row[0]}: {row[1]:.2f} minutes average wait time")
        
        # Query 3: Average ratings by provider specialty
        print("\nQuery 3: Average ratings by provider specialty")
        cursor.execute("""
        SELECT p.specialty, 
               AVG(f.provider_rating) as avg_provider_rating,
               AVG(f.overall_satisfaction) as avg_satisfaction
        FROM fact_feedback f
        JOIN dim_provider p ON f.provider_key = p.provider_key
        GROUP BY p.specialty
        ORDER BY avg_satisfaction DESC
        """)
        
        results = cursor.fetchall()
        for row in results:
            print(f"{row[0]}: Provider Rating: {row[1]:.2f}, Overall Satisfaction: {row[2]:.2f}")
        
        # Query 4: Technical issues by device type
        print("\nQuery 4: Technical issues by device type")
        cursor.execute("""
        SELECT d.device_type, 
               COUNT(*) as total_appointments,
               SUM(CASE WHEN a.had_technical_issues = 1 THEN 1 ELSE 0 END) as issues_count,
               (SUM(CASE WHEN a.had_technical_issues = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as issues_percentage
        FROM fact_appointment a
        JOIN dim_device d ON a.device_key = d.device_key
        GROUP BY d.device_type
        ORDER BY issues_percentage DESC
        """)
        
        results = cursor.fetchall()
        for row in results:
            print(f"{row[0]}: {row[2]} issues out of {row[1]} appointments ({row[3]:.2f}%)")
        
        cursor.close()
        return True
    except Exception as e:
        print(f"Error running sample queries: {e}")
        return False

def main():
    """Main function to build the data warehouse"""
    print("Starting data warehouse build process with SQLite...")
    start_time = time.time()
    
    # Create SQLite schema
    create_sqlite_schema()
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Create schema
        print("\nCreating schema...")
        if not execute_schema_file(conn):
            return
        
        # Load dimension tables
        print("\nLoading dimension tables...")
        load_dimension_table(conn, 'dim_date', 'dim_date.csv')
        load_dimension_table(conn, 'dim_time', 'dim_time.csv')
        load_dimension_table(conn, 'dim_provider', 'dim_provider.csv')
        load_dimension_table(conn, 'dim_patient', 'dim_patient.csv')
        load_dimension_table(conn, 'dim_status', 'dim_status.csv')
        load_dimension_table(conn, 'dim_device', 'dim_device.csv')
        
        # Load fact tables
        print("\nLoading fact tables...")
        load_fact_table(conn, 'fact_appointment', 'fact_appointment.csv')
        load_fact_table(conn, 'fact_feedback', 'fact_feedback.csv')
        
        # Verify data loading
        print("\nVerifying data loading...")
        verify_data_loading(conn)
        
        # Configure data retention
        print("\nConfiguring data retention policies...")
        configure_data_retention(conn)
        
        # Run sample queries
        run_sample_queries(conn)
        
        # Calculate execution time
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\nData warehouse build completed in {execution_time:.2f} seconds")
        print(f"Database file: {DB_FILE}")
        
    finally:
        # Close connection
        if conn:
            conn.close()
            print("Database connection closed")

if __name__ == "__main__":
    main()
