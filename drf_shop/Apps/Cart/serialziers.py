# @Time    : 2020/06/11
# @Author  : sunyingqiang
# @Email   :  344670075@qq.com
from rest_framework import serializers
from Apps.Goods.models import SKU


class CartSerializers(serializers.Serializer):
    """购物车添加数据序列化"""

    sku_id = serializers.IntegerField(label='sku_id', min_value=1)
    count = serializers.IntegerField(label='数量', min_value=1)
    selected = serializers.BooleanField(label='是否选中', default=True)

    def validate(self, attrs):
        try:
            sku = SKU.objects.get(id=attrs['sku_id'])
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return attrs


class GetCartSerializers(serializers.ModelSerializer):
    """获取购物车数据"""

    count = serializers.IntegerField(label='数量', min_value=1)
    selected = serializers.BooleanField(label='是否选中', default=True)
    goods = serializers.StringRelatedField(label='商品')
    category = serializers.StringRelatedField(label='从属类别')

    class Meta:
        model = SKU
        fields = '__all__'


class CartDeleteSerializers(serializers.Serializer):
    """删除购物车数据"""

    sku_id = serializers.IntegerField(label='商品id', min_value=1)

    def validated_sku_id(self, value):
        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return value

