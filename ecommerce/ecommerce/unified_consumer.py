from kafka import KafkaConsumer
import json
import logging
from users.models import User
from products.models import Product
# Import other models/services as necessary

logger = logging.getLogger(__name__)


class UnifiedConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'user_created', 
            'user_updated',
            'order_placed',
            'product_created',
            bootstrap_servers='localhost:9092',
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )

    def start_consuming(self):
        logger.info("Unified consumer started...")
        for message in self.consumer:
            topic = message.topic
            raw_message = message.value
            logger.info(f"Received message from topic {topic}")

            try:
                decoded_message = json.loads(raw_message.decode('utf-8'))
                self.process_message(topic, decoded_message)
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                logger.error(f"Error decoding message: {e}")

    def process_message(self, topic, event_data):
        if topic == 'user_created':
            self.process_user_created_event(event_data)
        elif topic == 'user_updated':
            self.process_user_updated_event(event_data)
        elif topic == 'order_placed':
            self.process_order_placed_event(event_data)
        elif topic == 'product_created':
            self.process_product_created_event(event_data)
        else:
            logger.warning(f"Unrecognized topic: {topic}")

    def process_user_created_event(self, event_data):
        logger.info(f"Processing user_created event: {event_data}")
        try:
            user_id = event_data['user_id']
            username = event_data['username']
            email = event_data['email']
            if User.objects.filter(id=user_id).exists():
                logger.warning(f"User with ID {user_id} already exists. Skipping creation.")
                return
            user = User(id=user_id, username=username, email=email)
            user.set_password("default_password")  # Handle password appropriately
            user.save()
            logger.info(f"User created: {user}")
        except KeyError as e:
            logger.error(f"Missing key in user_created event data: {e}")
        except Exception as e:
            logger.error(f"Error processing user_created event: {e}")

    def process_user_updated_event(self, event_data):
        logger.info(f"Processing user_updated event: {event_data}")
        try:
            user_id = event_data['user_id']
            username = event_data.get('username')
            email = event_data.get('email')
            user = User.objects.get(id=user_id)
            if username:
                user.username = username
            if email:
                user.email = email
            user.save()
            logger.info(f"User updated: {user}")
        except User.DoesNotExist:
            logger.warning(f"User with ID {user_id} does not exist. Cannot update.")
        except KeyError as e:
            logger.error(f"Missing key in user_updated event data: {e}")
        except Exception as e:
            logger.error(f"Error processing user_updated event: {e}")
    def process_order_placed_event(self,event_data):
        print("Debug:", event_data)  # Debug output for event data
        print("Calling order processing")

        # Check if 'items' key exists in the event data
        if 'items' in event_data:
            # Iterate through items in the order
            for item in event_data['items']:
                product_id = item['product_id']
                quantity = item['quantity']

                try:
                    product = Product.objects.get(id=product_id)
                    product.update_stock(quantity)  # Update stock using the quantity from the item
                    print(f"Stock updated for product {product_id}. New stock: {product.stock}")
                except Product.DoesNotExist:
                    print(f"Product with id {product_id} does not exist")
                except ValueError as e:
                    print(f"Error updating stock for product {product_id}: {e}")  # Handle insufficient stock
        else:
            # Handle the case where the event data has the simpler structure
            product_id = event_data.get('product_id')
            quantity = event_data.get('quantity')

            if product_id is not None and quantity is not None:
                try:
                    product = Product.objects.get(id=product_id)
                    product.update_stock(quantity)  # Update stock directly
                    print(f"Stock updated for product {product_id}. New stock: {product.stock}")
                except Product.DoesNotExist:
                    print(f"Product with id {product_id} does not exist")
                except ValueError as e:
                    print(f"Error updating stock for product {product_id}: {e}")  # Handle insufficient stock
            else:
                print("Event data does not contain valid product_id and quantity.")


    def process_product_created_event(self,event_data):
        print(f"Processing product_created event: {event_data}")  # Log incoming event data

        # Check for expected keys
        try:
            product_id = event_data['product_id']
            name = event_data['name']
            price = event_data['price']
            stock = event_data['stock']  # This is where you encountered the KeyError
            
            print(f"Attempting to create or get product with ID: {product_id}")
            print(f"Attempting to create or get product with ID: {product_id}")
            # Check if the product already exists before attempting to create
            existing_product = Product.objects.filter(id=product_id).first()
            if existing_product:
                print(f"Found existing product: {existing_product}")
                return  # Return early if the product exists

            # Logic to create a product in the database
            product = Product(
                id=product_id,
                name=name,
                price=price,
                stock=stock
            )
            product.save()  # Save the new product directly
            print(f"Product created: {product}")

        except KeyError as e:
            print(f"Missing key in event data: {e}")  # Handle missing keys
        except Exception as e:
            print(f"Error processing product_created event: {e}")  # Catch other errors

if __name__ == "__main__":
    consumer = UnifiedConsumer()
    consumer.start_consuming()
