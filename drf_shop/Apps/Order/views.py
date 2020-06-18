# @Time    : 2020/06/12
# @Author  : sunyingqiang
# @Email   : 344670075@qq.com
from decimal import Decimal
from django_redis import get_redis_connection
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import OrderSettlementSerializer
from Apps.Goods.models import SKU


class OrderSettlementView(APIView):
    """订单结算"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        redis_cli = get_redis_connection('cart')
        redis_cart = redis_cli.hgetall('cart_%s' % user.id)
        cart_selected = redis_cli.smembers('cart_selected_%s' % user.id)

        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]
        freight = Decimal('10.00')
        serializer = OrderSettlementSerializer({'freight': freight, 'skus': skus})
        return Response(serializer.data)

