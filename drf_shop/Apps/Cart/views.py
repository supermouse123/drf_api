# @Time    : 2020/06/12
# @Author  : sunyingqiang
# @Email   : 344670075@qq.com
import pickle
import base64
from django_redis import get_redis_connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serialziers import CartSerializers, GetCartSerializers, CartDeleteSerializers
from Apps.Goods.models import SKU
from drf_shop import contants


class CartView(APIView):
    """购物车"""

    def get(self, request):
        """获取"""

        try:
            user = request.user
        except Exception:
            user = None
        print(user)
        if user is not None and user.is_authenticated:
            redis_cli = get_redis_connection('cart')
            goods_object = redis_cli.hgetall('cart_%s' % user.id)
            redis_cart_selected = redis_cli.smembers('cart_selected_%s' % user.id)
            print(redis_cart_selected)
            cart = {}
            for sku_id, count in goods_object.items():
                cart[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_cart_selected     #判断是否在选中的列表中
                }

        else:
            cart = request.COOKIES.get('cart')

            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

        cart_sku = SKU.objects.filter(id__in=cart.keys())
        for sku in cart_sku:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']
        serializers = GetCartSerializers(cart_sku, many=True)

        return Response(serializers.data)


    def post(self, request):
        """添加"""

        serializers = CartSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)
        sku_id = serializers.validated_data.get('sku_id')
        count = serializers.validated_data.get('count')
        selected = serializers.validated_data.get('selected')

        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            redis_cli = get_redis_connection('cart')
            pl = redis_cli.pipeline()
            pl.hset('cart_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializers.data, status.HTTP_201_CREATED)
        else:
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

            sku = cart.get(sku_id)
            if sku:
                count = int(sku.get('count'))
            cart[sku_id] = {
                'count': count,
                'selected': selected
            }
            cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
            response = Response(serializers.data, status=status.HTTP_201_CREATED)
            response.set_cookie('cart', cookie_cart, max_age=contants.CART_COOKIE_EXPIRES)
            return response


    def put(self, request):
        """修改"""

        serializers = CartSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)
        sku_id = serializers.validated_data.get('sku_id')
        count = serializers.validated_data.get('count')
        selected = serializers.validated_data.get('selected')

        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            redis_cli = get_redis_connection('cart')
            pl = redis_cli.pipeline()
            pl.hset('cart_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializers.data, status.HTTP_201_CREATED)
        else:
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

            cart[sku_id] = {
                'count': int(count),
                'selected': selected
            }
            cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
            response = Response(serializers.data, status=status.HTTP_201_CREATED)
            response.set_cookie('cart', cookie_cart, max_age=contants.CART_COOKIE_EXPIRES)
            return response


    def delete(self, request):
        """删除购物车数据"""

        serializer = CartDeleteSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']
        print(sku_id)
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            redis_cli = get_redis_connection('cart')
            pl = redis_cli.pipeline()
            pl.hdel('cart_%s' % user.id, sku_id)
            pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(status.HTTP_204_NO_CONTENT)
        else:
            cart = request.COOKIES.get('cart')
            response = Response(status.HTTP_204_NO_CONTENT)

            print(cart)
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                print(cart)
                if sku_id in cart:
                    del cart[sku_id]
                    print('-----', cart)
                    cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                    response.set_cookie('cart', cookie_cart, max_age=contants.CART_COOKIE_EXPIRES)
            return response


def user_merge_cart(request, response):
    """购物车合并"""
    cart = request.COOKIES.get('cart')
    if not cart:
        return response
    user = request.user
    redis_cli = get_redis_connection('cart')
    pl = redis_cli.pipeline()

    if cart is not None:
        cart = pickle.loads(base64.b64decode(cart.encode()))

    for sku_id in cart:
        pl.hset('cart_%s' % user.id, sku_id, cart[sku_id]['count'])
        if cart[sku_id]['selected']:
            pl.sadd('cart_selected_%s' % user.id, sku_id)
        else:
            pl.srem('cart_selected_%s' % user.id, sku_id)
    pl.execute()
    response.delete_cookie('cart')

    return response




