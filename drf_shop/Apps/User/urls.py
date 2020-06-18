# @Time    : 2020/06/09
# @Author  : sunyingqiang
# @Email   :  344670075@qq.com
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Apps.User.views.user_register import RegisterView, SendSmsCodeView, \
                                          LoginView, UserDetailView, \
                                          UserLogoutView
from Apps.User.views.user_address import UserAddressViewSet

router = DefaultRouter()
router.register('address', UserAddressViewSet, basename='address')

urlpatterns = [
    path(r'register', RegisterView.as_view()),
    path(r'send_sms_code', SendSmsCodeView.as_view()),
    path(r'login', LoginView.as_view()),
    path(r'detail', UserDetailView.as_view()),
    path(r'logout', UserLogoutView.as_view()),
    path(r'', include(router.urls)),
]