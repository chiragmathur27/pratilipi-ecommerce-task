from django.core.management.base import BaseCommand
from products.consumer import listen_for_orders

class Command(BaseCommand):
    help = 'Listen to Kafka topic for order events'

    def handle(self, *args, **kwargs):
        listen_for_orders()