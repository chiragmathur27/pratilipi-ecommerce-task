from django.core.management.base import BaseCommand
from ecommerce.unified_consumer import UnifiedConsumer

class Command(BaseCommand):
    help = 'Starts the unified Kafka consumer for user and product events'

    def handle(self, *args, **kwargs):
        consumer = UnifiedConsumer()
        consumer.start_consuming()
