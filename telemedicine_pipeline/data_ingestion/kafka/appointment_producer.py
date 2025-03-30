import json
import time
import os
from kafka import KafkaProducer
from datetime import datetime, timedelta
import random
import pandas as pd

# Configure Kafka producer
def create_kafka_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda v: v.encode('utf-8') if v else None
        )
        print("Kafka producer created successfully")
        return producer
    except Exception as e:
        print(f"Error creating Kafka producer: {e}")
        return None

# Load appointment data
def load_appointment_data():
    try:
        df = pd.read_csv('../data_sources/appointment_logs/appointment_logs.csv')
        print(f"Loaded {len(df)} appointment records")
        return df
    except Exception as e:
        print(f"Error loading appointment data: {e}")
        return pd.DataFrame()

# Simulate real-time appointment events
def simulate_appointment_events(producer, appointments_df):
    # Topics
    appointment_topic = "telemedicine-appointments"
    events_topic = "telemedicine-events"
    
    # Event types
    event_types = [
        "appointment_scheduled", 
        "patient_login", 
        "provider_login", 
        "session_started", 
        "session_ended", 
        "technical_issue",
        "appointment_cancelled",
        "appointment_rescheduled"
    ]
    
    # Get a sample of appointments to simulate
    sample_appointments = appointments_df.sample(min(100, len(appointments_df)))
    
    print(f"Simulating events for {len(sample_appointments)} appointments...")
    
    for _, appointment in sample_appointments.iterrows():
        # Send the appointment data
        appointment_id = appointment['appointment_id']
        producer.send(appointment_topic, key=appointment_id, value=appointment.to_dict())
        
        # Simulate a sequence of events for this appointment
        appointment_date = datetime.strptime(appointment['appointment_date'], '%Y-%m-%d')
        scheduled_time = appointment['scheduled_time']
        
        # Base timestamp for the appointment
        base_timestamp = datetime.combine(appointment_date.date(), 
                                         datetime.strptime(scheduled_time, '%H:%M:%S').time())
        
        # Generate a sequence of events
        events = []
        
        # Appointment scheduled (happened in the past)
        events.append({
            "event_type": "appointment_scheduled",
            "appointment_id": appointment_id,
            "patient_id": appointment["patient_id"],
            "provider_id": appointment["provider_id"],
            "timestamp": (base_timestamp - timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d %H:%M:%S"),
            "details": {
                "scheduled_time": scheduled_time,
                "appointment_type": appointment["appointment_type"]
            }
        })
        
        # If appointment was cancelled or rescheduled, add that event
        if appointment["status"] == "Cancelled":
            events.append({
                "event_type": "appointment_cancelled",
                "appointment_id": appointment_id,
                "patient_id": appointment["patient_id"],
                "provider_id": appointment["provider_id"],
                "timestamp": (base_timestamp - timedelta(hours=random.randint(1, 24))).strftime("%Y-%m-%d %H:%M:%S"),
                "details": {
                    "reason": random.choice(["Patient request", "Provider unavailable", "Emergency", "Other"])
                }
            })
        elif appointment["status"] == "Rescheduled":
            events.append({
                "event_type": "appointment_rescheduled",
                "appointment_id": appointment_id,
                "patient_id": appointment["patient_id"],
                "provider_id": appointment["provider_id"],
                "timestamp": (base_timestamp - timedelta(hours=random.randint(1, 24))).strftime("%Y-%m-%d %H:%M:%S"),
                "details": {
                    "original_time": scheduled_time,
                    "new_time": (datetime.strptime(scheduled_time, '%H:%M:%S') + 
                                timedelta(days=random.randint(1, 7))).strftime('%H:%M:%S'),
                    "reason": random.choice(["Patient request", "Provider unavailable", "Emergency", "Other"])
                }
            })
        
        # For completed appointments, simulate the full flow
        if appointment["status"] == "Completed":
            # Patient login
            patient_login_time = base_timestamp - timedelta(minutes=random.randint(5, 15))
            events.append({
                "event_type": "patient_login",
                "appointment_id": appointment_id,
                "patient_id": appointment["patient_id"],
                "timestamp": patient_login_time.strftime("%Y-%m-%d %H:%M:%S"),
                "details": {
                    "device_type": appointment["device_type"],
                    "operating_system": appointment["operating_system"],
                    "browser": appointment["browser"]
                }
            })
            
            # Provider login
            provider_login_time = base_timestamp - timedelta(minutes=random.randint(0, 5))
            events.append({
                "event_type": "provider_login",
                "appointment_id": appointment_id,
                "provider_id": appointment["provider_id"],
                "timestamp": provider_login_time.strftime("%Y-%m-%d %H:%M:%S"),
                "details": {
                    "device_type": random.choice(["Laptop", "Desktop"]),
                    "operating_system": random.choice(["Windows", "macOS"]),
                    "browser": random.choice(["Chrome", "Firefox", "Edge"])
                }
            })
            
            # Session started
            session_start_time = base_timestamp + timedelta(minutes=appointment["wait_time_minutes"])
            events.append({
                "event_type": "session_started",
                "appointment_id": appointment_id,
                "patient_id": appointment["patient_id"],
                "provider_id": appointment["provider_id"],
                "timestamp": session_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "details": {
                    "connection_quality": appointment["connection_quality"],
                    "wait_time_minutes": appointment["wait_time_minutes"]
                }
            })
            
            # Technical issues (if any)
            if appointment["had_technical_issues"]:
                issue_time = session_start_time + timedelta(minutes=random.randint(1, 10))
                events.append({
                    "event_type": "technical_issue",
                    "appointment_id": appointment_id,
                    "timestamp": issue_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "details": {
                        "issue_type": appointment["technical_issue_type"],
                        "severity": random.choice(["Low", "Medium", "High"]),
                        "resolved": random.choice([True, False])
                    }
                })
            
            # Session ended
            session_end_time = session_start_time + timedelta(minutes=appointment["duration_minutes"])
            events.append({
                "event_type": "session_ended",
                "appointment_id": appointment_id,
                "patient_id": appointment["patient_id"],
                "provider_id": appointment["provider_id"],
                "timestamp": session_end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "details": {
                    "duration_minutes": appointment["duration_minutes"],
                    "ended_normally": not appointment["had_technical_issues"] or random.random() > 0.3
                }
            })
        
        # Sort events by timestamp
        events.sort(key=lambda x: x["timestamp"])
        
        # Send events to Kafka
        for event in events:
            producer.send(events_topic, key=appointment_id, value=event)
            print(f"Sent event: {event['event_type']} for appointment {appointment_id}")
            time.sleep(0.1)  # Small delay between events
        
        # Flush after each appointment's events
        producer.flush()
        print(f"Completed sending events for appointment {appointment_id}")
        time.sleep(0.5)  # Delay between appointments

def main():
    # Create Kafka producer
    producer = create_kafka_producer()
    if not producer:
        return
    
    # Load appointment data
    appointments_df = load_appointment_data()
    if appointments_df.empty:
        return
    
    # Simulate appointment events
    simulate_appointment_events(producer, appointments_df)
    
    # Close the producer
    producer.close()
    print("Kafka producer closed")

if __name__ == "__main__":
    main()
