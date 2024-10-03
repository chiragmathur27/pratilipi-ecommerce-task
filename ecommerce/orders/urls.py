from django.urls import path
from .views import OrderView

urlpatterns = [
    path('', OrderView.as_view(), name='order-list'),
    path('<int:order_id>/', OrderView.as_view(), name='order-detail'),
]
