from . models import Order
from .serializers import OrderSerializer
from rest_framework.views import APIView
from rest_framework import filters, generics, permissions
# Create your views here.

class OrderList(generics.ListAPIView):
    serializer_class = OrderSerializer
    def get_queryset(self):
        return Order.objects.filter(enabled=True).order_by('id')
