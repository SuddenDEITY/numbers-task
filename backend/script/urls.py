from django.urls import path
from .views import OrderList

urlpatterns = [
        path('api/', OrderList.as_view(), name='orders'),
]