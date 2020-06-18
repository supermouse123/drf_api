# @Time    : 2020/06/09
# @Author  : sunyingqiang
# @Email   :  344670075@qq.com
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from Apps.User.serializers.user_address_serializers import UserAddressSerializer
from Apps.User.models import Address
from drf_shop import contants


class UserAddressViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         GenericViewSet):
    """用户地址视图类"""

    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)


    def list(self, request, *args, **kwargs):
        """展示用户地址"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': contants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data
        })


    def create(self, request, *args, **kwargs):
        """创建用户地址"""
        count = request.user.addresses.count()
        if count >= contants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status.HTTP_400_BAD_REQUEST)

        return super().create(self, request, *args, **kwargs)


    def destroy(self, request, *args, **kwargs):
        """地址删除"""
        address = self.get_object()
        address.is_deleted = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """设置默认地址  url:/api/user/address/<pk>/status/"""
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)


    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """修改标题 url:/api/user/address/<pk>/title/"""
        address = self.get_object()
        serializer = UserAddressSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)




