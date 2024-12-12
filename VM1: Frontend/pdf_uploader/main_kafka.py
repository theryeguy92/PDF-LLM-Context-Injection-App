from kafka import KafkaProducer
import json

# Kafka Configuration
KAFKA_BROKER_URL = "172.31.9.51:9092"
KAFKA_TOPIC = "pdf_data"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Test Sending a Message
try:
    producer.send(KAFKA_TOPIC, {"test_key": "test_value"})
    producer.flush()
    print("Message sent successfully!")
except Exception as e:
    print(f"Error sending message: {e}")
