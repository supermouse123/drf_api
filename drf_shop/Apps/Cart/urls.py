from django.urls import path, include
from Apps.Cart.views import CartView
# from rest_framework.routers import DefaultRouter
#
# router = DefaultRouter()
# router.register('cart', CartView, basename='cart')


urlpatterns = [
   path(r'', CartView.as_view())
   # path(r'', include(router.urls)),
]