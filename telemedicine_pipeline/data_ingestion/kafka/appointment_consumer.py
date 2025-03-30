import json
import os
import pandas as pd
from datetime import datetime
from kafka import KafkaConsumer

# Configure Kafka consumer
def create_kafka_consumer(topics):
    try:
        consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='telemedicine-consumer-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            key_deserializer=lambda x: x.decode('utf-8') if x else None
        )
        print(f"Kafka consumer created successfully for topics: {topics}")
        return consumer
    except Exception as e:
        print(f"Error creating Kafka consumer: {e}")
        return None

# Process and validate appointment data
def validate_appointment(appointment):
    """Validate appointment data and return errors if any"""
    errors = []
    
    # Check required fields
    required_fields = ['appointment_id', 'provider_id', 'patient_id', 'appointment_date', 
                      'scheduled_time', 'appointment_type', 'status']
    
    for field in required_fields:
        if field not in appointment or appointment[field] is None:
            errors.append(f"Missing required field: {field}")
    
    # Validate appointment status
    valid_statuses = ["Completed", "Cancelled", "No-show", "Rescheduled"]
    if 'status' in appointment and appointment['status'] not in valid_statuses:
        errors.append(f"Invalid status: {appointment['status']}")
    
    # Validate wait time and duration based on status
    if appointment.get('status') == "Completed":
        if 'wait_time_minutes' not in appointment or appointment['wait_time_minutes'] is None:
            errors.append("Completed appointment missing wait_time_minutes")
        if 'duration_minutes' not in appointment or appointment['duration_minutes'] is None:
            errors.append("Completed appointment missing duration_minutes")
    
    return errors

# Process and validate event data
def validate_event(event):
    """Validate event data and return errors if any"""
    errors = []
    
    # Check required fields
    required_fields = ['event_type', 'appointment_id', 'timestamp']
    
    for field in required_fields:
        if field not in event or event[field] is None:
            errors.append(f"Missing required field: {field}")
    
    # Validate event type
    valid_event_types = [
        "appointment_scheduled", "patient_login", "provider_login", 
        "session_started", "session_ended", "technical_issue",
        "appointment_cancelled", "appointment_rescheduled"
    ]
    
    if 'event_type' in event and event['event_type'] not in valid_event_types:
        errors.append(f"Invalid event_type: {event['event_type']}")
    
    # Validate timestamp format
    if 'timestamp' in event:
        try:
            datetime.strptime(event['timestamp'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            errors.append(f"Invalid timestamp format: {event['timestamp']}")
    
    return errors

# Save data to disk
def save_data(data, data_type, data_id):
    """Save data to appropriate directory based on type"""
    base_dir = '/home/ubuntu/telemedicine_pipeline/data_ingestion/processed'
    
    # Create directories if they don't exist
    os.makedirs(f"{base_dir}/appointments", exist_ok=True)
    os.makedirs(f"{base_dir}/events", exist_ok=True)
    os.makedirs(f"{base_dir}/errors", exist_ok=True)
    
    # Format current timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    if data_type == 'appointment':
        filename = f"{base_dir}/appointments/appointment_{data_id}_{timestamp}.json"
    elif data_type == 'event':
        filename = f"{base_dir}/events/event_{data_id}_{timestamp}.json"
    elif data_type == 'error':
        filename = f"{base_dir}/errors/error_{data_id}_{timestamp}.json"
    else:
        print(f"Unknown data type: {data_type}")
        return
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved {data_type} data to {filename}")

def main():
    # Create directories for processed data
    os.makedirs('/home/ubuntu/telemedicine_pipeline/data_ingestion/processed', exist_ok=True)
    
    # Create Kafka consumer
    topics = ['telemedicine-appointments', 'telemedicine-events']
    consumer = create_kafka_consumer(topics)
    
    if not consumer:
        return
    
    print("Starting to consume messages...")
    
    try:
        for message in consumer:
            topic = message.topic
            key = message.key
            value = message.value
            
            print(f"Received message from topic {topic} with key {key}")
            
            # Process based on topic
            if topic == 'telemedicine-appointments':
                # Validate appointment data
                errors = validate_appointment(value)
                
                if errors:
                    print(f"Validation errors in appointment {key}: {errors}")
                    error_data = {
                        'data_type': 'appointment',
                        'data_id': key,
                        'errors': errors,
                        'original_data': value
                    }
                    save_data(error_data, 'error', key)
                else:
                    # Save valid appointment data
                    save_data(value, 'appointment', key)
            
            elif topic == 'telemedicine-events':
                # Validate event data
                errors = validate_event(value)
                
                if errors:
                    print(f"Validation errors in event for appointment {key}: {errors}")
                    error_data = {
                        'data_type': 'event',
                        'data_id': key,
                        'errors': errors,
                        'original_data': value
                    }
                    save_data(error_data, 'error', key)
                else:
                    # Save valid event data
                    event_type = value.get('event_type', 'unknown')
                    event_id = f"{key}_{event_type}"
                    save_data(value, 'event', event_id)
    
    except KeyboardInterrupt:
        print("Consumer stopped by user")
    finally:
        consumer.close()
        print("Kafka consumer closed")

if __name__ == "__main__":
    main()
