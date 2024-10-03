from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Order
from .serializers import OrderSerializer
from .producer import publish_order_created

class OrderView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.using('orders_db').filter(user_id=self.request.user.id)

    def get(self, request, order_id=None):
        if order_id:
            try:
                order = self.get_queryset().get(id=order_id)
                serializer = OrderSerializer(order)
                return Response(serializer.data)
            except Order.DoesNotExist:
                return Response({'error': 'Order not found'}, status=404)
        else:
            orders = self.get_queryset()
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            
            # Publish the order created event to Kafka
            order_data = {
                'order_id': order.id,
                'user_id': order.user_id,
                'items': request.data.get('items'),  # Pass the order items
            }
            publish_order_created(order_data)  # Kafka producer publishes the event

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, order_id):
        try:
            order = self.get_queryset().get(id=order_id)
            serializer = OrderSerializer(order, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

    def delete(self, request, order_id):
        try:
            order = self.get_queryset().get(id=order_id)
            order.delete()
            return Response(status=204)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
