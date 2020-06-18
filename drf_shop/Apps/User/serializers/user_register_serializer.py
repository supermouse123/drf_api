# @Time    : 2020/06/09
# @Author  : sunyingqiang
# @Email   :  344670075@qq.com
import re
from rest_framework import serializers
from Apps.User.models import User
from django_redis import get_redis_connection


class RegisterSerializers(serializers.ModelSerializer):
    username = serializers.CharField(min_length=5,
                                     max_length=20,
                                     error_messages={
                                         'min_length': '用户名为5-20个字符',
                                         'max_length': '用户名为5-20个字符'
                                     })
    password = serializers.CharField(write_only=True,   #表明该字段仅用于反序列化输入，默认False
                                     min_length=8,
                                     max_length=20,
                                     error_messages={
                                         'min_length': '密码为8-20个字符',
                                         'max_length': '密码为8-20个字符'
                                     })
    mobile = serializers.CharField()
    password2 = serializers.CharField(write_only=True)
    sms_code = serializers.CharField(write_only=True)  #验证码
    allow = serializers.CharField(write_only=True, error_messages={'blank': '必须同意协议'})     #是否同意用户协议
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'mobile', 'email', 'sms_code', 'allow']

    def validate_username(self, value):
        try:
            user = User.objects.get(username=value)
        except:
            user = None
        if user:
            raise serializers.ValidationError('用户名已存在')
        return value

    def validated_mobile(self, value):
        try:
            user = User.objects.get(mobile=value)
        except:
            user = None
        if user:
            raise serializers.ValidationError('此手机号已经被注册')

        if not re.match('^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')
        return value

    def validated_allow(self, value):
        if not value:
            raise serializers.ValidationError('必须同意协议')
        return value

    def validate(self, attrs):
        redis_cli = get_redis_connection('default')
        key = 'sms_code_' + attrs.get('mobile')
        sms_code_redis = redis_cli.get(key)
        if not sms_code_redis:
            raise serializers.ValidationError('验证码已过期')
        redis_cli.delete(key)
        sms_code_redis = sms_code_redis.decode()
        sms_code_request = attrs.get('sms_code')
        if sms_code_redis != sms_code_request:
            raise serializers.ValidationError('验证码错误')

        pwd1 = attrs.get('password')
        pwd2 = attrs.get('password2')
        if pwd1 != pwd2:
            raise serializers.ValidationError('两次输入的密码不一致')

        return attrs

    def create(self, validated_data):
        del validated_data['allow']        #去除数据库中没有的字段
        del validated_data['password2']
        del validated_data['sms_code']
        user = super().create(validated_data)
        user.set_password(validated_data['password'])   #密码加密
        user.save()
        return user


class LoginSerializers(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


    def validate(self, attrs):
        print(attrs)
        try:
            if re.match('^1[3-9]\d{9}$', attrs['username']):
                # 帐号为手机号
                user = User.objects.get(mobile=attrs['username'])
            else:
                # 帐号为用户名
                user = User.objects.get(username=attrs['username'])
        except User.DoesNotExist:
            raise serializers.ValidationError('用户不存在')
        else:
            if user.check_password(attrs['password']):
                return attrs
            else:
                raise serializers.ValidationError('用户密码错误')


class DetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'mobile', 'email', 'create_time')










