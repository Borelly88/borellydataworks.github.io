import boto3
import json
import os
import pandas as pd
from datetime import datetime
from botocore.exceptions import ClientError

# Mock S3 client for local development
class MockS3Client:
    def __init__(self, local_directory):
        self.local_directory = local_directory
        os.makedirs(self.local_directory, exist_ok=True)
        print(f"Initialized mock S3 client with local directory: {local_directory}")
    
    def list_objects_v2(self, Bucket, Prefix):
        """List objects in the local directory that match the prefix"""
        prefix_path = os.path.join(self.local_directory, Prefix)
        prefix_dir = os.path.dirname(prefix_path)
        
        # If prefix directory doesn't exist, return empty list
        if not os.path.exists(prefix_dir):
            return {'Contents': []}
        
        contents = []
        for root, _, files in os.walk(prefix_dir):
            for file in files:
                if file.endswith('.json'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.local_directory)
                    if rel_path.startswith(Prefix):
                        contents.append({
                            'Key': rel_path,
                            'LastModified': datetime.fromtimestamp(os.path.getmtime(full_path)),
                            'Size': os.path.getsize(full_path)
                        })
        
        return {'Contents': contents}
    
    def get_object(self, Bucket, Key):
        """Get object from the local directory"""
        file_path = os.path.join(self.local_directory, Key)
        try:
            with open(file_path, 'rb') as f:
                return {'Body': f}
        except FileNotFoundError:
            raise ClientError({'Error': {'Code': 'NoSuchKey', 'Message': 'The specified key does not exist.'}}, 'GetObject')

# Function to connect to S3 (or mock S3 for local development)
def get_s3_client():
    """Get S3 client (or mock client for local development)"""
    # For local development, use mock S3 client
    local_directory = '/home/ubuntu/telemedicine_pipeline/data_sources'
    return MockS3Client(local_directory)

# Function to list feedback files in S3
def list_feedback_files(s3_client, bucket_name, prefix='patient_feedback/'):
    """List all feedback files in the S3 bucket with the given prefix"""
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        if 'Contents' not in response:
            print(f"No files found in bucket {bucket_name} with prefix {prefix}")
            return []
        
        # Filter for JSON files
        json_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.json')]
        print(f"Found {len(json_files)} JSON files in bucket {bucket_name} with prefix {prefix}")
        return json_files
    
    except ClientError as e:
        print(f"Error listing objects in bucket {bucket_name}: {e}")
        return []

# Function to read feedback data from S3
def read_feedback_data(s3_client, bucket_name, file_key):
    """Read feedback data from S3 file"""
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        content = response['Body'].read().decode('utf-8')
        feedback_data = json.loads(content)
        return feedback_data
    
    except ClientError as e:
        print(f"Error reading file {file_key} from bucket {bucket_name}: {e}")
        return None

# Function to validate feedback data
def validate_feedback(feedback):
    """Validate feedback data and return errors if any"""
    errors = []
    
    # Check required fields
    required_fields = ['feedback_id', 'appointment_id', 'patient_id', 'provider_id', 
                      'feedback_date', 'overall_satisfaction']
    
    for field in required_fields:
        if field not in feedback or feedback[field] is None:
            errors.append(f"Missing required field: {field}")
    
    # Validate ratings (should be 1-5)
    rating_fields = ['provider_rating', 'ease_of_use_rating', 
                     'audio_quality_rating', 'video_quality_rating', 'overall_satisfaction']
    
    for field in rating_fields:
        if field in feedback and feedback[field] is not None:
            rating = feedback[field]
            if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                errors.append(f"Invalid rating value for {field}: {rating}")
    
    return errors

# Function to process feedback files
def process_feedback_files(bucket_name='telemedicine-data', prefix='patient_feedback/'):
    """Process all feedback files from S3"""
    # Get S3 client
    s3_client = get_s3_client()
    
    # List feedback files
    feedback_files = list_feedback_files(s3_client, bucket_name, prefix)
    
    if not feedback_files:
        print("No feedback files to process")
        return
    
    # Create directory for processed feedback
    processed_dir = '/home/ubuntu/telemedicine_pipeline/data_ingestion/processed/feedback'
    os.makedirs(processed_dir, exist_ok=True)
    
    # Process each feedback file
    valid_feedback = []
    error_feedback = []
    
    for file_key in feedback_files:
        print(f"Processing feedback file: {file_key}")
        
        # Read feedback data
        feedback_data = read_feedback_data(s3_client, bucket_name, file_key)
        
        if not feedback_data:
            continue
        
        # Validate feedback data
        errors = validate_feedback(feedback_data)
        
        if errors:
            print(f"Validation errors in feedback {feedback_data.get('feedback_id', 'unknown')}: {errors}")
            error_data = {
                'data_type': 'feedback',
                'data_id': feedback_data.get('feedback_id', 'unknown'),
                'errors': errors,
                'original_data': feedback_data
            }
            error_feedback.append(error_data)
        else:
            valid_feedback.append(feedback_data)
    
    # Save valid feedback to CSV
    if valid_feedback:
        valid_df = pd.DataFrame(valid_feedback)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        valid_file = f"{processed_dir}/valid_feedback_{timestamp}.csv"
        valid_df.to_csv(valid_file, index=False)
        print(f"Saved {len(valid_feedback)} valid feedback records to {valid_file}")
    
    # Save error feedback to JSON
    if error_feedback:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        error_file = f"{processed_dir}/error_feedback_{timestamp}.json"
        with open(error_file, 'w') as f:
            json.dump(error_feedback, f, indent=2)
        print(f"Saved {len(error_feedback)} error feedback records to {error_file}")

if __name__ == "__main__":
    process_feedback_files()
