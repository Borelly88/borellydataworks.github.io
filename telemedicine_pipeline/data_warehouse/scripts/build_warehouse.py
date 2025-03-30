import os
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time
from datetime import datetime

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 5439,  # Redshift-compatible PostgreSQL port
    'user': 'redshift',
    'password': 'redshift',
    'database': 'redshift'
}

# Paths
TRANSFORMED_DATA_DIR = '/home/ubuntu/telemedicine_pipeline/data_processing/transformed'
SCHEMA_FILE = '/home/ubuntu/telemedicine_pipeline/data_warehouse/schemas/telemedicine_schema.sql'

def connect_to_database():
    """Connect to the Redshift-compatible PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=DB_PARAMS['host'],
            port=DB_PARAMS['port'],
            user=DB_PARAMS['user'],
            password=DB_PARAMS['password'],
            database=DB_PARAMS['database']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print(f"Connected to database {DB_PARAMS['database']} on {DB_PARAMS['host']}:{DB_PARAMS['port']}")
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
        cursor.execute(schema_sql)
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
        
        # Get column names
        columns = df.columns.tolist()
        
        # Prepare SQL statement
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join([f'"{col}"' for col in columns])
        
        # Insert data
        cursor = conn.cursor()
        
        # Convert DataFrame to list of tuples
        data = [tuple(row) for row in df.values]
        
        # Execute batch insert
        insert_query = f'INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})'
        cursor.executemany(insert_query, data)
        
        cursor.close()
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
        
        # Get column names
        columns = df.columns.tolist()
        
        # Prepare SQL statement
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join([f'"{col}"' for col in columns])
        
        # Insert data
        cursor = conn.cursor()
        
        # Convert DataFrame to list of tuples
        data = [tuple(row) for row in df.values]
        
        # Execute batch insert
        insert_query = f'INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})'
        
        # Insert in batches to avoid memory issues
        batch_size = 1000
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            cursor.executemany(insert_query, batch)
            print(f"Inserted batch {i//batch_size + 1} of {(len(data) + batch_size - 1) // batch_size}")
        
        cursor.close()
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
        
        # Insert or update retention policies
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
            INSERT INTO data_retention_policies (table_name, retention_period_days, last_cleanup_date)
            VALUES (%s, %s, CURRENT_DATE)
            ON CONFLICT (table_name) 
            DO UPDATE SET 
                retention_period_days = EXCLUDED.retention_period_days,
                updated_at = CURRENT_TIMESTAMP
            """, (table, days))
        
        cursor.close()
        print("Data retention policies configured")
        return True
    except Exception as e:
        print(f"Error configuring data retention policies: {e}")
        return False

def create_data_loading_procedure(conn):
    """Create a stored procedure for regular data loading"""
    try:
        cursor = conn.cursor()
        
        # Create a procedure to load data incrementally
        cursor.execute("""
        CREATE OR REPLACE PROCEDURE load_incremental_data(load_date DATE)
        LANGUAGE plpgsql
        AS $$
        BEGIN
            -- Log the start of the procedure
            RAISE NOTICE 'Starting incremental load for date %', load_date;
            
            -- Insert code here to load incremental data
            -- This would typically involve:
            -- 1. Loading new dimension records
            -- 2. Loading new fact records
            -- 3. Updating any changed dimension records (slowly changing dimensions)
            
            -- For demonstration purposes, we'll just log the completion
            RAISE NOTICE 'Completed incremental load for date %', load_date;
        END;
        $$;
        """)
        
        cursor.close()
        print("Data loading procedure created")
        return True
    except Exception as e:
        print(f"Error creating data loading procedure: {e}")
        return False

def main():
    """Main function to build the data warehouse"""
    print("Starting data warehouse build process...")
    start_time = time.time()
    
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
        
        # Create data loading procedure
        print("\nCreating data loading procedure...")
        create_data_loading_procedure(conn)
        
        # Calculate execution time
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\nData warehouse build completed in {execution_time:.2f} seconds")
        
    finally:
        # Close connection
        if conn:
            conn.close()
            print("Database connection closed")

if __name__ == "__main__":
    main()
