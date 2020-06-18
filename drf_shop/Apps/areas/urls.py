# @Time    : 2020/06/09
# @Author  : sunyingqiang
# @Email   :  344670075@qq.com
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'areas', views.AreaViewSet, basename='areas')
urlpatterns = [
    path('', include(router.urls)),
]