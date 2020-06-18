# @Time    : 2020/06/12
# @Author  : sunyingqiang
# @Email   : 344670075@qq.com
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from Apps.Goods.models import SKU
from .models import OrderInfo, OrderGoods


class CartSKUSerializer(serializers.ModelSerializer):
    """购物车商品序列化"""

    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')


class OrderSettlementSerializer(serializers.Serializer):
    """订单结算数据序列化"""

    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)


class SaveOrderSerializer(serializers.ModelSerializer):
    """下单数据序列化"""

    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        """保存订单"""

        user = self.context['request'].user
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        address = validated_data['address']
        pay_method = validated_data['pay_method']
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal(0),
                    pay_method=pay_method,
                    freight=Decimal(10),
                    status=OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                    if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']
                    else OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                )
                redis_cli = get_redis_connection('cart')
                redis_cart = redis_cli.hgetall('cart_%s' % user.id)
                cart_selected = redis_cli.smembers('cart_selected_%s' % user.id)

                cart = {}
                for sku_id in cart_selected:
                    cart[int(sku_id)] = int(redis_cart[sku_id])
                skus = SKU.objects.filter(id__in=cart.keys())
                for sku in skus:
                    sku_count = cart[sku.id]
                    origin_stock = sku.stock
                    origin_sales = sku.sales

                    if sku_count > origin_stock:
                        transaction.savepoint_rollback(save_id)
                        raise serializers.ValidationError('商品库存不足')

                    #减少库存
                    new_stock = origin_stock - sku_count
                    new_sales = origin_sales + sku_count

                    sku.stock = new_stock
                    sku.sales = new_sales
                    sku.save()

                    #累计商品的SPU销量信息
                    sku.goods.sales += sku_count
                    sku.goods.save()

                    #累计订单基本信息数据
                    order.total_count += sku_count
                    order.total_amount += (sku.price * sku_count)

                    #保存订单商品
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=sku_count,
                        price=sku.price
                    )
                    order.total_amount += order.freight
                    order.save()
            except ValidationError:
                raise
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise
            transaction.savepoint_commit(save_id)
            pl = redis_cli.pipeline()
            pl.hdel('cart_%s' % user.id, *cart_selected)
            pl.srem('cart_selected_%s' % user.id, *cart_selected)
            pl.execute()
            return order