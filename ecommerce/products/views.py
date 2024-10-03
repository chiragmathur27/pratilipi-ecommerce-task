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
