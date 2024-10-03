# # orders/serializers.py
# from rest_framework import serializers
# from .models import Order, OrderItem

# class OrderItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ['product_id', 'quantity', 'price']

# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True)
#     total = serializers.SerializerMethodField()
#     user_id = serializers.IntegerField(read_only=True)

#     class Meta:
#         model = Order
#         fields = ['id', 'user_id', 'items', 'created_at', 'updated_at', 'status', 'total']

#     def get_total(self, obj):
#         return sum(item.quantity * item.price for item in obj.items.all())

#     def create(self, validated_data):
#         items_data = validated_data.pop('items')
#         order = Order.objects.create(**validated_data)
#         for item_data in items_data:
#             OrderItem.objects.create(order=order, **item_data)
#         return order

#     def update(self, instance, validated_data):
#         items_data = validated_data.pop('items', None)
#         instance = super().update(instance, validated_data)
#         if items_data is not None:
#             instance.items.all().delete()
#             for item_data in items_data:
#                 OrderItem.objects.create(order=instance, **item_data)
#         return instance

# from rest_framework import serializers
# from .models import Order, OrderItem
# from products.models import Product

# class OrderItemSerializer(serializers.ModelSerializer):
#     product_details = serializers.SerializerMethodField()

#     class Meta:
#         model = OrderItem
#         fields = ['product_id', 'quantity', 'price', 'product_details']

#     def get_product_details(self, obj):
#         try:
#             product = Product.objects.using('products_db').get(id=obj.product_id)
#             return {
#                 'name': product.name,
#                 'description': product.description
#             }
#         except Product.DoesNotExist:
#             return None

# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True)
#     total = serializers.SerializerMethodField()
#     user_id = serializers.IntegerField(read_only=True)

#     class Meta:
#         model = Order
#         fields = ['id', 'user_id', 'items', 'created_at', 'updated_at', 'status', 'total']

#     def get_total(self, obj):
#         return sum(item.quantity * item.price for item in obj.items.all())

#     def create(self, validated_data):
#         items_data = validated_data.pop('items')
#         order = Order.objects.create(**validated_data)
        
#         for item_data in items_data:
#             # Verify product exists in products database
#             product_id = item_data['product_id']
#             try:
#                 product = Product.objects.using('products_db').get(id=product_id)
#                 OrderItem.objects.create(
#                     order=order,
#                     product_id=product_id,
#                     quantity=item_data['quantity'],
#                     price=product.price
#                 )
#             except Product.DoesNotExist:
#                 order.delete()
#                 raise serializers.ValidationError(f"Product with id {product_id} does not exist")
        
#         return order

# from django.db import transaction
# from rest_framework import serializers
# from .models import Order, OrderItem
# from products.models import Product

# class OrderItemSerializer(serializers.ModelSerializer):
#     product_details = serializers.SerializerMethodField()

#     class Meta:
#         model = OrderItem
#         fields = ['product_id', 'quantity', 'price', 'product_details']

#     def get_product_details(self, obj):
#         try:
#             product = Product.objects.using('products_db').get(id=obj.product_id)
#             return {
#                 'name': product.name,
#                 'description': product.description
#             }
#         except Product.DoesNotExist:
#             return None
# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True)
#     total = serializers.SerializerMethodField()
#     user_id = serializers.IntegerField(read_only=True)

#     class Meta:
#         model = Order
#         fields = ['id', 'user_id', 'items', 'created_at', 'updated_at', 'status', 'total']

#     def get_total(self, obj):
#         return sum(item.quantity * item.price for item in obj.items.all())

#     @transaction.atomic  # Use a transaction to ensure all-or-nothing
#     def create(self, validated_data):
#         items_data = validated_data.pop('items')
#         order = Order.objects.create(**validated_data)
        
#         for item_data in items_data:
#             product_id = item_data['product_id']
#             try:
#                 product = Product.objects.using('products_db').get(id=product_id)  # Query the products database
#                 OrderItem.objects.create(
#                     order=order,
#                     product_id=product_id,
#                     quantity=item_data['quantity'],
#                     price=product.price  # Set price from the product
#                 )
#             except Product.DoesNotExist:
#                 order.delete()  # Rollback the order if any product is invalid
#                 raise serializers.ValidationError(f"Product with id {product_id} does not exist")
        
#         return order

from django.db import transaction
from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_details = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity', 'price', 'product_details']

    def get_product_details(self, obj):
        try:
            product = Product.objects.using('products_db').get(id=obj.product_id)
            return {
                'name': product.name,
                'description': product.description
            }
        except Product.DoesNotExist:
            return None

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user_id', 'items', 'created_at', 'updated_at', 'status', 'total']
        extra_kwargs = {
            'user_id': {'required': True},  # Ensure user_id is required
        }

    def get_total(self, obj):
        return sum(item.quantity * item.price for item in obj.items.all())

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user_id = validated_data.pop('user_id')  # Ensure user_id is extracted correctly
        order = Order.objects.create(user_id=user_id, **validated_data)

        for item_data in items_data:
            product_id = item_data['product_id']
            try:
                product = Product.objects.using('products_db').get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product_id=product_id,
                    quantity=item_data['quantity'],
                    price=product.price
                )
            except Product.DoesNotExist:
                order.delete()
                raise serializers.ValidationError(f"Product with id {product_id} does not exist")

        return order
