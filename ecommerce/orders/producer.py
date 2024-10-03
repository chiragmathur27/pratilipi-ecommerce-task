# orders/producer.py
from kafka import KafkaProducer
import json

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers='localhost:9092',  # Kafka server address
        value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize message to JSON
    )

def publish_order_created(order_data):
    print("order placed event")
    producer = get_kafka_producer()
    producer.send('order_placed', order_data)
    producer.flush()
