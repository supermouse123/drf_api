from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer
from .models import SKU, GoodsCategory
from .search_indexes import SKUIndex


class GoodsCategorySerializer(serializers.ModelSerializer):
    """商品分类序列化"""

    class Meta:
        model = GoodsCategory
        fields = ('id', )


class SKUSerializer(serializers.ModelSerializer):
    """商品列表页序列化"""

    category = GoodsCategorySerializer()
    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments', 'category')


class SKUIndexSerializer(HaystackSerializer):
    """sku索引结果数据序列化器"""

    object = SKUSerializer(read_only=True)

    class Meta:
        index_classes = [SKUIndex]
        fields = (
            'text',  #接收查询关键字
            'object'  #用于返回查询结果
        )


class GoodsDetailSerializer(serializers.ModelSerializer):
    """商品详情序列化"""

    goods = serializers.StringRelatedField(label='商品')
    category = serializers.StringRelatedField(label='从属类别')

    class Meta:
        model = SKU
        fields = '__all__'


class HistorySerializer(serializers.ModelSerializer):
    """用户浏览记录序列化"""

    goods = serializers.StringRelatedField(label='商品')
    category = serializers.StringRelatedField(label='从属类别')

    class Meta:
        model = SKU
        fields = '__all__'