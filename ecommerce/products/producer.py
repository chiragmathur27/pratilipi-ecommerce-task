from kafka import KafkaProducer
import json

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize messages as JSON
    )

def send_product_created_event(product_id, name, price, stock):
    from .models import Product  # Import here to avoid circular dependency
    producer = get_kafka_producer()
    event_data = {
        "product_id": product_id,
        "name": name,
        "price": str(price),
        "stock": stock
    }
    producer.send('product_created', value=event_data)
    producer.flush()  # Ensure the message is sent

