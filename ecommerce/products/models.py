from django.db import models
from .producer import get_kafka_producer

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)  # Inventory management
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'products'

    def __str__(self):
        return f"{self.name} {self.description}"

    def update_stock(self, quantity):
        if self.stock < quantity:
            print(f"Current stock: {self.stock}, Requested quantity: {quantity}")
            raise ValueError("Insufficient stock")
        self.stock -= quantity
        self.save()
        self.emit_inventory_updated_event()

    def add_stock(self, quantity):
        self.stock += quantity
        self.save()
        self.emit_inventory_updated_event()

    def emit_inventory_updated_event(self):
        producer = get_kafka_producer()
        event_data = {
            "product_id": self.id,
            "updated_stock": self.stock
        }
        producer.send('inventory_updated', value=event_data)
        producer.flush()  # Ensure the message is sent

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the parent save method
        self.emit_product_created_event()


    def emit_product_created_event(self):
        producer = get_kafka_producer()
        event_data = {
            "product_id": self.id,
            "name": self.name,
            "price": str(self.price),
            "stock":self.stock
        }
        producer.send('product_created', value=event_data)
        producer.flush()  # Ensure the message is sent

# from django.db import models
# from .producer import send_product_created_event, get_kafka_producer
# from django.db import models

# class Product(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     stock = models.IntegerField(default=0)  # Inventory management
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         app_label = 'products'

#     def __str__(self):
#         return f"{self.name} {self.description}"

#     def update_stock(self, quantity):
#         if self.stock < quantity:
#             print(f"Current stock: {self.stock}, Requested quantity: {quantity}")
#             raise ValueError("Insufficient stock")
#         self.stock -= quantity
#         self.save(update_fields=['stock'])  # Only update stock
#         self.emit_inventory_updated_event()

#     def add_stock(self, quantity):
#         self.stock += quantity
#         self.save(update_fields=['stock'])  # Only update stock
#         self.emit_inventory_updated_event()

#     def emit_inventory_updated_event(self):
#         producer = get_kafka_producer()
#         event_data = {
#             "product_id": self.id,
#             "updated_stock": self.stock
#         }
#         producer.send('inventory_updated', value=event_data)
#         producer.flush()  # Ensure the message is sent

#     def save(self, *args, **kwargs):
#         # Check if the instance is being created
#         if self.pk is None:  # Only emit event if this is a new product
#             super().save(*args, **kwargs)  # Save first to get the ID
#             send_product_created_event(self.id, self.name, self.price, self.stock)  # Emit event after saving
#         else:
#             super().save(*args, **kwargs)  # Update existing instance

#     @staticmethod
#     def process_order_placed_event(event_data):
#         product_id = event_data['product_id']
#         quantity = event_data['quantity']

#         try:
#             product = Product.objects.get(id=product_id)
#             product.update_stock(quantity)
#         except Product.DoesNotExist:
#             print(f"Product with id {product_id} does not exist")
#         except ValueError as e:
#             # Handle insufficient stock case
#             print(f"Error updating stock for product {product_id}: {e}")
