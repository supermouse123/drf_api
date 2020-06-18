# @Time    : 2020/06/09
# @Author  : sunyingqiang
# @Email   :  344670075@qq.com
import random
from django.contrib.auth import login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from Apps.User.models import User

from django_redis import get_redis_connection
from Apps.User.serializers.user_register_serializer import RegisterSerializers, \
                                                           LoginSerializers, \
                                                           DetailSerializers
from drf_shop import contants
from celery_tasks.tasks import send_register_active_email
from Apps.Cart.views import user_merge_cart


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    关闭csrf验证
    """

    def enforce_csrf(self, request):
        return


class RegisterView(CreateAPIView):
    """用户注册视图"""

    serializer_class = RegisterSerializers


class SendSmsCodeView(APIView):
    """发送验证码"""

    def get(self, request):
        mobile = request.query_params.get('mobile')
        email = request.query_params.get('email')
        redis_cli = get_redis_connection('default')
        if redis_cli.get('sms_flag_' + mobile):
            return Response({'errmsg': '验证码60秒之后才能发送'})
        sms_code = random.randint(100000, 999999)
        redis_pipeline = redis_cli.pipeline()
        redis_pipeline.setex('sms_code_' + mobile, contants.SMS_CODE_EXPIRES, sms_code)
        # 保存60秒发送标记
        redis_pipeline.setex('sms_flag_' + mobile, contants.SMS_FLAG_EXPIRES, 1)
        redis_pipeline.execute()
        send_register_active_email.delay(email, sms_code)
        return Response({'message': 'ok'})


class LoginView(APIView):
    """用户登录视图"""

    authentication_classes = (CsrfExemptSessionAuthentication,)
    def post(self, request):
        data = request.data
        serializers = LoginSerializers(data=data)
        if serializers.is_valid(raise_exception=True):
            user = User.objects.get(username=serializers.validated_data['username'])
            login(request, user)
            response = Response(serializers.validated_data)
            user_merge_cart(request, response)
            return response
        else:
            return Response(serializers.error_messages)


class UserDetailView(RetrieveAPIView):
    """用户详情页视图"""

    serializer_class = DetailSerializers
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


"""
url.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()  #只有继承ViewSet才能用
router.register(r'detail', UserDetailView, basename='detail')


class UserDetailView(mixins.RetrieveModelMixin, GenericViewSet):
    #使用mixin类用户详情页视图

    serializer_class = DetailSerializers
    lookup_field = 'username'         #指定路由后面按什么查
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.all()
"""




class UserLogoutView(APIView):
    """退出登录视图"""

    def get(self, request):
        logout(request)
        return Response({'message': '退出成功'})












