from django.urls import path, include
from .views import OrderSettlementView

urlpatterns = [
    path('settlement', OrderSettlementView.as_view())
]