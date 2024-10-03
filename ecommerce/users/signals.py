# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .models import User
from kafka import KafkaProducer
import json
# User = get_user_model()


@receiver(post_save, sender=User)
def user_registered(sender, instance, created, **kwargs):
    if created:
        print(f"User {instance.email} has registered.")
        
        # Kafka producer logic
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092', 
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        event_data = {
            'event': 'user_registered',
            'user': instance.email
        }
        
        # Send Kafka message
        producer.send('user_events', event_data)
        producer.flush()