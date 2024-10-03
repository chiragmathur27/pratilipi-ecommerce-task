# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Product
# from .serializers import ProductSerializer
# from django.shortcuts import get_object_or_404
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication
# # from .kafka_utils import publish_event  # Assuming you saved the Kafka publisher in a module named kafka_utils

# class ProductView(APIView):
#     """
#     API View to handle product CRUD operations.
#     """
#     authentication_classes = (JWTAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     def get(self, request, product_id=None):
#         """
#         Get a single product by ID or all products.
#         """
#         if product_id:
#             product = get_object_or_404(Product, id=product_id)
#             serializer = ProductSerializer(product)
#             return Response(serializer.data)
#         else:
#             products = Product.objects.all()
#             serializer = ProductSerializer(products, many=True)
#             return Response(serializer.data)

#     def post(self, request):
#         """
#         Create a new product.
#         """
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             product = serializer.save()
            
#             # Publish "Product Created" event to Kafka
#             event_data = {
#                 'event': 'Product Created',
#                 'product': serializer.data
#             }
#             # publish_event('product-events', event_data)

#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, product_id):
#         """
#         Update an existing product.
#         """
#         product = get_object_or_404(Product, id=product_id)
#         serializer = ProductSerializer(product, data=request.data, partial=True)
#         if serializer.is_valid():
#             product = serializer.save()

#             # Publish "Product Updated" event to Kafka
#             event_data = {
#                 'event': 'Product Updated',
#                 'product': serializer.data
#             }
#             # publish_event('product-events', event_data)

#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, product_id):
#         """
#         Delete a product.
#         """
#         product = get_object_or_404(Product, id=product_id)
#         product.delete()

#         # Publish "Product Deleted" event to Kafka
#         event_data = {
#             'event': 'Product Deleted',
#             'product_id': product_id
#         }
#         # publish_event('product-events', event_data)

#         return Response(status=status.HTTP_204_NO_CONTENT)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product  # Import the create_product function
from .serializers import ProductSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .producer import send_product_created_event
class ProductView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Product.objects.using('products_db')

    def get(self, request, product_id=None):
        if product_id:
            product = get_object_or_404(self.get_queryset(), id=product_id)  # Simplified using get_object_or_404
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        else:
            products = self.get_queryset()
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            # Create the product
            new_product = serializer.save()
            
            # Emit the product created event
            send_product_created_event(new_product.id, new_product.name, new_product.price, new_product.stock)

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    def put(self, request, product_id):
        product = get_object_or_404(self.get_queryset(), id=product_id)
        
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, product_id):
        product = get_object_or_404(self.get_queryset(), id=product_id)
        product.delete()
        return Response(status=204)
