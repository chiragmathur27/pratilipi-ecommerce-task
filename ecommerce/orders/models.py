from django.db import models

class Order(models.Model):
    user_id = models.IntegerField()  # Store the user ID instead of a ForeignKey
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled')
    ], default='PENDING')

    def __str__(self):
        return f"Order {self.id} by User {self.user_id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_id = models.IntegerField()  # Store the product ID instead of a ForeignKey
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of Product {self.product_id} in Order {self.order.id}"
    
    class Meta:
        app_label = 'orders'
