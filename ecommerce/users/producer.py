# from confluent_kafka import Producer
# import json

# def kafka_producer():
#     p = Producer({'bootstrap.servers': 'localhost:9092'})
#     return p

# def send_user_created_event(user):
#     producer = kafka_producer()
#     event_data = {
#         'event': 'user_created',
#         'user_id': user.id,
#         'email': user.email,
#         'username': user.username
#     }
#     producer.produce('user_events', key=str(user.id), value=json.dumps(event_data).encode('utf-8'))
#     producer.flush()

from kafka import KafkaProducer
import json

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers='localhost:9092',  # Adjust to your Kafka server address
        value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize JSON messages
    )
    
def send_user_created_event(user_id, username, email):
    producer = get_kafka_producer()
    event_data = {
        "user_id": user_id,
        "username": username,
        "email": email
    }
    producer.send('user_created', value=event_data)
    producer.flush()  # Ensure the message is sent
