import os
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Define paths
TRANSFORMED_DIR = '/home/ubuntu/telemedicine_pipeline/data_processing/transformed'
OUTPUT_DIR = '/home/ubuntu/telemedicine_pipeline/data_processing/quality_checks'

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_transformed_data():
    """Load all transformed data files"""
    data = {}
    
    # List of expected files
    expected_files = [
        'dim_date.csv',
        'dim_time.csv',
        'dim_provider.csv',
        'dim_patient.csv',
        'dim_status.csv',
        'dim_device.csv',
        'fact_appointment.csv',
        'fact_feedback.csv'
    ]
    
    # Load each file
    for file in expected_files:
        file_path = os.path.join(TRANSFORMED_DIR, file)
        if os.path.exists(file_path):
            data[file.replace('.csv', '')] = pd.read_csv(file_path)
            print(f"Loaded {file} with {len(data[file.replace('.csv', '')])} rows")
        else:
            print(f"Warning: File not found - {file_path}")
            data[file.replace('.csv', '')] = pd.DataFrame()
    
    return data

def check_primary_keys(data):
    """Check for duplicate primary keys in dimension and fact tables"""
    results = {}
    
    # Check dimension tables
    for table_name in ['dim_date', 'dim_time', 'dim_provider', 'dim_patient', 'dim_status', 'dim_device']:
        if table_name in data and not data[table_name].empty:
            df = data[table_name]
            key_col = f"{table_name.replace('dim_', '')}_key" if table_name != 'dim_date' and table_name != 'dim_time' else f"{table_name.replace('dim_', '')}_id"
            
            if key_col in df.columns:
                duplicates = df[df.duplicated(key_col)]
                results[table_name] = {
                    'has_duplicates': len(duplicates) > 0,
                    'duplicate_count': len(duplicates),
                    'duplicate_keys': duplicates[key_col].tolist() if len(duplicates) > 0 else []
                }
            else:
                results[table_name] = {
                    'error': f"Key column {key_col} not found in {table_name}"
                }
        else:
            results[table_name] = {
                'error': f"Table {table_name} not found or empty"
            }
    
    # Check fact tables
    for table_name in ['fact_appointment', 'fact_feedback']:
        if table_name in data and not data[table_name].empty:
            df = data[table_name]
            key_col = 'appointment_id' if table_name == 'fact_appointment' else 'feedback_id'
            
            if key_col in df.columns:
                duplicates = df[df.duplicated(key_col)]
                results[table_name] = {
                    'has_duplicates': len(duplicates) > 0,
                    'duplicate_count': len(duplicates),
                    'duplicate_keys': duplicates[key_col].tolist() if len(duplicates) > 0 else []
                }
            else:
                results[table_name] = {
                    'error': f"Key column {key_col} not found in {table_name}"
                }
        else:
            results[table_name] = {
                'error': f"Table {table_name} not found or empty"
            }
    
    return results

def check_foreign_keys(data):
    """Check foreign key relationships between fact and dimension tables"""
    results = {}
    
    # Check appointment fact foreign keys
    if 'fact_appointment' in data and not data['fact_appointment'].empty:
        appointment_fact = data['fact_appointment']
        
        # Check provider_key
        if 'dim_provider' in data and not data['dim_provider'].empty and 'provider_key' in appointment_fact.columns:
            provider_keys = set(data['dim_provider']['provider_key'])
            appointment_provider_keys = set(appointment_fact['provider_key'].dropna())
            invalid_keys = appointment_provider_keys - provider_keys
            
            results['appointment_provider_fk'] = {
                'has_invalid': len(invalid_keys) > 0,
                'invalid_count': len(invalid_keys),
                'invalid_keys': list(invalid_keys)
            }
        
        # Check patient_key
        if 'dim_patient' in data and not data['dim_patient'].empty and 'patient_key' in appointment_fact.columns:
            patient_keys = set(data['dim_patient']['patient_key'])
            appointment_patient_keys = set(appointment_fact['patient_key'].dropna())
            invalid_keys = appointment_patient_keys - patient_keys
            
            results['appointment_patient_fk'] = {
                'has_invalid': len(invalid_keys) > 0,
                'invalid_count': len(invalid_keys),
                'invalid_keys': list(invalid_keys)
            }
        
        # Check date_id
        if 'dim_date' in data and not data['dim_date'].empty and 'date_id' in appointment_fact.columns:
            date_ids = set(data['dim_date']['date_id'])
            appointment_date_ids = set(appointment_fact['date_id'].dropna())
            invalid_ids = appointment_date_ids - date_ids
            
            results['appointment_date_fk'] = {
                'has_invalid': len(invalid_ids) > 0,
                'invalid_count': len(invalid_ids),
                'invalid_ids': list(invalid_ids)
            }
        
        # Check time_id
        if 'dim_time' in data and not data['dim_time'].empty and 'time_id' in appointment_fact.columns:
            time_ids = set(data['dim_time']['time_id'])
            appointment_time_ids = set(appointment_fact['time_id'].dropna())
            invalid_ids = appointment_time_ids - time_ids
            
            results['appointment_time_fk'] = {
                'has_invalid': len(invalid_ids) > 0,
                'invalid_count': len(invalid_ids),
                'invalid_ids': list(invalid_ids)
            }
        
        # Check status_key
        if 'dim_status' in data and not data['dim_status'].empty and 'status_key' in appointment_fact.columns:
            status_keys = set(data['dim_status']['status_key'])
            appointment_status_keys = set(appointment_fact['status_key'].dropna())
            invalid_keys = appointment_status_keys - status_keys
            
            results['appointment_status_fk'] = {
                'has_invalid': len(invalid_keys) > 0,
                'invalid_count': len(invalid_keys),
                'invalid_keys': list(invalid_keys)
            }
        
        # Check device_key
        if 'dim_device' in data and not data['dim_device'].empty and 'device_key' in appointment_fact.columns:
            device_keys = set(data['dim_device']['device_key'])
            appointment_device_keys = set(appointment_fact['device_key'].dropna())
            invalid_keys = appointment_device_keys - device_keys
            
            results['appointment_device_fk'] = {
                'has_invalid': len(invalid_keys) > 0,
                'invalid_count': len(invalid_keys),
                'invalid_keys': list(invalid_keys)
            }
    
    # Check feedback fact foreign keys
    if 'fact_feedback' in data and not data['fact_feedback'].empty:
        feedback_fact = data['fact_feedback']
        
        # Check provider_key
        if 'dim_provider' in data and not data['dim_provider'].empty and 'provider_key' in feedback_fact.columns:
            provider_keys = set(data['dim_provider']['provider_key'])
            feedback_provider_keys = set(feedback_fact['provider_key'].dropna())
            invalid_keys = feedback_provider_keys - provider_keys
            
            results['feedback_provider_fk'] = {
                'has_invalid': len(invalid_keys) > 0,
                'invalid_count': len(invalid_keys),
                'invalid_keys': list(invalid_keys)
            }
        
        # Check patient_key
        if 'dim_patient' in data and not data['dim_patient'].empty and 'patient_key' in feedback_fact.columns:
            patient_keys = set(data['dim_patient']['patient_key'])
            feedback_patient_keys = set(feedback_fact['patient_key'].dropna())
            invalid_keys = feedback_patient_keys - patient_keys
            
            results['feedback_patient_fk'] = {
                'has_invalid': len(invalid_keys) > 0,
                'invalid_count': len(invalid_keys),
                'invalid_keys': list(invalid_keys)
            }
        
        # Check date_id
        if 'dim_date' in data and not data['dim_date'].empty and 'date_id' in feedback_fact.columns:
            date_ids = set(data['dim_date']['date_id'])
            feedback_date_ids = set(feedback_fact['date_id'].dropna())
            invalid_ids = feedback_date_ids - date_ids
            
            results['feedback_date_fk'] = {
                'has_invalid': len(invalid_ids) > 0,
                'invalid_count': len(invalid_ids),
                'invalid_ids': list(invalid_ids)
            }
        
        # Check appointment_id (relationship to appointment fact)
        if 'fact_appointment' in data and not data['fact_appointment'].empty:
            appointment_ids = set(data['fact_appointment']['appointment_id'])
            feedback_appointment_ids = set(feedback_fact['appointment_id'].dropna())
            invalid_ids = feedback_appointment_ids - appointment_ids
            
            results['feedback_appointment_fk'] = {
                'has_invalid': len(invalid_ids) > 0,
                'invalid_count': len(invalid_ids),
                'invalid_ids': list(invalid_ids)
            }
    
    return results

def check_data_quality(data):
    """Check data quality issues in fact tables"""
    results = {}
    
    # Check appointment fact data quality
    if 'fact_appointment' in data and not data['fact_appointment'].empty:
        appointment_fact = data['fact_appointment']
        
        # Check for negative wait times
        if 'wait_time_minutes' in appointment_fact.columns:
            negative_wait_times = appointment_fact[appointment_fact['wait_time_minutes'] < 0]
            results['negative_wait_times'] = {
                'has_issues': len(negative_wait_times) > 0,
                'issue_count': len(negative_wait_times),
                'affected_ids': negative_wait_times['appointment_id'].tolist() if len(negative_wait_times) > 0 else []
            }
        
        # Check for negative durations
        if 'duration_minutes' in appointment_fact.columns:
            negative_durations = appointment_fact[appointment_fact['duration_minutes'] < 0]
            results['negative_durations'] = {
                'has_issues': len(negative_durations) > 0,
                'issue_count': len(negative_durations),
                'affected_ids': negative_durations['appointment_id'].tolist() if len(negative_durations) > 0 else []
            }
        
        # Check for missing required fields
        required_fields = ['appointment_id', 'date_id', 'status_key']
        for field in required_fields:
            if field in appointment_fact.columns:
                missing_values = appointment_fact[appointment_fact[field].isna()]
                results[f'missing_{field}'] = {
                    'has_issues': len(missing_values) > 0,
                    'issue_count': len(missing_values),
                    'affected_rows': len(missing_values)
                }
    
    # Check feedback fact data quality
    if 'fact_feedback' in data and not data['fact_feedback'].empty:
        feedback_fact = data['fact_feedback']
        
        # Check for invalid ratings (outside 1-5 range)
        rating_fields = ['provider_rating', 'ease_of_use_rating', 'audio_quality_rating', 
                         'video_quality_rating', 'overall_satisfaction']
        
        for field in rating_fields:
            if field in feedback_fact.columns:
                invalid_ratings = feedback_fact[
                    (feedback_fact[field] < 1) | (feedback_fact[field] > 5) & (~feedback_fact[field].isna())
                ]
                results[f'invalid_{field}'] = {
                    'has_issues': len(invalid_ratings) > 0,
                    'issue_count': len(invalid_ratings),
                    'affected_ids': invalid_ratings['feedback_id'].tolist() if len(invalid_ratings) > 0 else []
                }
        
        # Check for missing required fields
        required_fields = ['feedback_id', 'appointment_id', 'date_id']
        for field in required_fields:
            if field in feedback_fact.columns:
                missing_values = feedback_fact[feedback_fact[field].isna()]
                results[f'missing_{field}'] = {
                    'has_issues': len(missing_values) > 0,
                    'issue_count': len(missing_values),
                    'affected_rows': len(missing_values)
                }
    
    return results

def generate_summary_report(pk_results, fk_results, dq_results):
    """Generate a summary report of all data quality checks"""
    summary = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'primary_key_checks': {
            'tables_checked': len(pk_results),
            'tables_with_issues': sum(1 for table, result in pk_results.items() 
                                     if 'has_duplicates' in result and result['has_duplicates']),
            'total_duplicate_keys': sum(result.get('duplicate_count', 0) for result in pk_results.values()),
            'details': pk_results
        },
        'foreign_key_checks': {
            'relationships_checked': len(fk_results),
            'relationships_with_issues': sum(1 for rel, result in fk_results.items() 
                                           if 'has_invalid' in result and result['has_invalid']),
            'total_invalid_keys': sum(result.get('invalid_count', 0) for result in fk_results.values()),
            'details': fk_results
        },
        'data_quality_checks': {
            'checks_performed': len(dq_results),
            'checks_with_issues': sum(1 for check, result in dq_results.items() 
                                     if 'has_issues' in result and result['has_issues']),
            'total_quality_issues': sum(result.get('issue_count', 0) for result in dq_results.values()),
            'details': dq_results
        }
    }
    
    return summary

def main():
    print("Starting data quality checks...")
    
    # Load transformed data
    print("\nLoading transformed data...")
    data = load_transformed_data()
    
    # Run data quality checks
    print("\nChecking primary keys...")
    pk_results = check_primary_keys(data)
    
    print("\nChecking foreign keys...")
    fk_results = check_foreign_keys(data)
    
    print("\nChecking data quality...")
    dq_results = check_data_quality(data)
    
    # Generate summary report
    print("\nGenerating summary report...")
    summary = generate_summary_report(pk_results, fk_results, dq_results)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Save summary report
    summary_file = os.path.join(OUTPUT_DIR, f'quality_check_summary_{timestamp}.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nData quality check complete! Summary saved to {summary_file}")
    
    # Print summary
    print("\nSummary of data quality checks:")
    print(f"Primary key checks: {summary['primary_key_checks']['tables_with_issues']} tables with issues out of {summary['primary_key_checks']['tables_checked']}")
    print(f"Foreign key checks: {summary['foreign_key_checks']['relationships_with_issues']} relationships with issues out of {summary['foreign_key_checks']['relationships_checked']}")
    print(f"Data quality checks: {summary['data_quality_checks']['checks_with_issues']} checks with issues out of {summary['data_quality_checks']['checks_performed']}")
    
    return summary

if __name__ == "__main__":
    main()
