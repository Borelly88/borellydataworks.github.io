import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta

# Mock external API for telemedicine appointment logs
class TelemedicineExternalAPI:
    def __init__(self, base_url=None):
        # For local development, we'll use the local data files
        self.base_data_dir = '/home/ubuntu/telemedicine_pipeline/data_sources'
        print(f"Initialized mock external API using local data directory: {self.base_data_dir}")
    
    def get_appointments(self, start_date=None, end_date=None, limit=100):
        """
        Get appointment data from the external API
        In this mock implementation, we'll read from our local CSV file
        """
        try:
            # Read the appointment logs CSV
            appointments_file = os.path.join(self.base_data_dir, 'appointment_logs/appointment_logs.csv')
            appointments_df = pd.read_csv(appointments_file)
            
            # Filter by date if provided
            if start_date:
                appointments_df = appointments_df[appointments_df['appointment_date'] >= start_date]
            if end_date:
                appointments_df = appointments_df[appointments_df['appointment_date'] <= end_date]
            
            # Limit the number of records
            if limit and limit < len(appointments_df):
                appointments_df = appointments_df.sample(limit)
            
            # Convert to list of dictionaries
            appointments = appointments_df.to_dict(orient='records')
            
            return {
                'status': 'success',
                'data': appointments,
                'count': len(appointments)
            }
        
        except Exception as e:
            print(f"Error getting appointments: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_appointment_details(self, appointment_id):
        """
        Get details for a specific appointment
        In this mock implementation, we'll read from our local JSON files
        """
        try:
            # Try to find the appointment JSON file
            appointment_file = os.path.join(
                self.base_data_dir, 
                f'appointment_logs/appointment_{appointment_id}.json'
            )
            
            if os.path.exists(appointment_file):
                with open(appointment_file, 'r') as f:
                    appointment = json.load(f)
                
                return {
                    'status': 'success',
                    'data': appointment
                }
            else:
                # If not found, try to find it in the CSV
                appointments_file = os.path.join(self.base_data_dir, 'appointment_logs/appointment_logs.csv')
                appointments_df = pd.read_csv(appointments_file)
                
                # Filter by appointment ID
                appointment = appointments_df[appointments_df['appointment_id'] == appointment_id]
                
                if len(appointment) > 0:
                    return {
                        'status': 'success',
                        'data': appointment.iloc[0].to_dict()
                    }
                else:
                    return {
                        'status': 'error',
                        'message': f'Appointment with ID {appointment_id} not found'
                    }
        
        except Exception as e:
            print(f"Error getting appointment details: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_provider_schedule(self, provider_id, start_date=None, end_date=None):
        """
        Get schedule for a specific provider
        In this mock implementation, we'll filter the appointment logs
        """
        try:
            # Read the appointment logs CSV
            appointments_file = os.path.join(self.base_data_dir, 'appointment_logs/appointment_logs.csv')
            appointments_df = pd.read_csv(appointments_file)
            
            # Filter by provider ID
            provider_appointments = appointments_df[appointments_df['provider_id'] == provider_id]
            
            # Filter by date if provided
            if start_date:
                provider_appointments = provider_appointments[provider_appointments['appointment_date'] >= start_date]
            if end_date:
                provider_appointments = provider_appointments[provider_appointments['appointment_date'] <= end_date]
            
            # Sort by date and time
            provider_appointments = provider_appointments.sort_values(by=['appointment_date', 'scheduled_time'])
            
            # Convert to list of dictionaries
            appointments = provider_appointments.to_dict(orient='records')
            
            return {
                'status': 'success',
                'data': appointments,
                'count': len(appointments)
            }
        
        except Exception as e:
            print(f"Error getting provider schedule: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

# Function to fetch and process data from the external API
def fetch_from_external_api(days_back=7):
    """
    Fetch appointment data from the external API for the specified number of days back
    """
    # Create API client
    api_client = TelemedicineExternalAPI()
    
    # Calculate date range
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    print(f"Fetching appointments from {start_date} to {end_date}")
    
    # Get appointments
    response = api_client.get_appointments(start_date=start_date, end_date=end_date)
    
    if response['status'] == 'success':
        appointments = response['data']
        print(f"Retrieved {len(appointments)} appointments from external API")
        
        # Create directory for processed data
        processed_dir = '/home/ubuntu/telemedicine_pipeline/data_ingestion/processed/external_api'
        os.makedirs(processed_dir, exist_ok=True)
        
        # Save to CSV
        if appointments:
            df = pd.DataFrame(appointments)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            output_file = f"{processed_dir}/appointments_{timestamp}.csv"
            df.to_csv(output_file, index=False)
            print(f"Saved {len(appointments)} appointments to {output_file}")
        else:
            print("No appointments to save")
    else:
        print(f"Error fetching appointments: {response.get('message', 'Unknown error')}")

# Function to fetch provider schedules
def fetch_provider_schedules(provider_ids=None, days_forward=14):
    """
    Fetch provider schedules from the external API for the specified providers
    """
    # Create API client
    api_client = TelemedicineExternalAPI()
    
    # If no provider IDs specified, use a default list
    if not provider_ids:
        # Read the provider data CSV to get provider IDs
        providers_file = os.path.join('/home/ubuntu/telemedicine_pipeline/data_sources', 'provider_data/providers.csv')
        providers_df = pd.read_csv(providers_file)
        
        # Filter for active providers
        active_providers = providers_df[providers_df['active'] == True]
        
        # Get provider IDs
        provider_ids = active_providers['provider_id'].tolist()[:10]  # Limit to 10 providers for demo
    
    # Calculate date range
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=days_forward)).strftime('%Y-%m-%d')
    
    print(f"Fetching schedules for {len(provider_ids)} providers from {start_date} to {end_date}")
    
    # Create directory for processed data
    processed_dir = '/home/ubuntu/telemedicine_pipeline/data_ingestion/processed/provider_schedules'
    os.makedirs(processed_dir, exist_ok=True)
    
    # Fetch schedule for each provider
    all_schedules = []
    
    for provider_id in provider_ids:
        print(f"Fetching schedule for provider {provider_id}")
        
        response = api_client.get_provider_schedule(
            provider_id=provider_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if response['status'] == 'success':
            schedule = response['data']
            print(f"Retrieved {len(schedule)} appointments for provider {provider_id}")
            all_schedules.extend(schedule)
        else:
            print(f"Error fetching schedule for provider {provider_id}: {response.get('message', 'Unknown error')}")
    
    # Save all schedules to CSV
    if all_schedules:
        df = pd.DataFrame(all_schedules)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_file = f"{processed_dir}/provider_schedules_{timestamp}.csv"
        df.to_csv(output_file, index=False)
        print(f"Saved {len(all_schedules)} scheduled appointments to {output_file}")
    else:
        print("No scheduled appointments to save")

if __name__ == "__main__":
    # Fetch appointments from the last 7 days
    fetch_from_external_api(days_back=7)
    
    # Fetch provider schedules for the next 14 days
    fetch_provider_schedules(days_forward=14)
