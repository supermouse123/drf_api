from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_haystack.viewsets import HaystackViewSet
from django_redis import get_redis_connection
from .serializers import SKUSerializer, SKUIndexSerializer, GoodsDetailSerializer, HistorySerializer
from .models import SKU
from drf_shop.contants import USER_BROWSING_HISTORY_COUNTS_LIMIT

class CustomPage(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20


class SKUListView(ListAPIView):
    """
    sku商品视图类
    RetrieveModelMixin只能返回一个结果
    ListModelMixin可以返回多个结果
    """

    serializer_class = SKUSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('create_time', 'price', 'sales')
    pagination_class = CustomPage

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)


class SKUSearchViewSet(HaystackViewSet):
    """SKU搜索"""

    index_models = [SKU]
    serializer_class = SKUIndexSerializer


class GoodsDetailViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    """商品详情页视图"""

    serializer_class = GoodsDetailSerializer

    def get_queryset(self):
        return SKU.objects.all()

    def retrieve(self, request, *args, **kwargs):
        goods_id = self.kwargs['pk']
        user = request.user
        print(user.id)
        if user.is_authenticated:
            redis_cli = get_redis_connection('default')
            history_key = 'history_%d' % user.id
            redis_cli.lrem(history_key, 0, goods_id)  #去重
            redis_cli.lpush(history_key, goods_id)
            redis_cli.ltrim(history_key, 0, USER_BROWSING_HISTORY_COUNTS_LIMIT)  #设置保存多少条
        return super().retrieve(self, request, *args, **kwargs)


class GetUserHistoryView(ListAPIView):
    """获取用户浏览记录"""

    permission_classes = [IsAuthenticated]
    serializer_class = HistorySerializer

    def get_queryset(self):
        user_id = self.request.user.id
        redis_cli = get_redis_connection('default')
        history_key = 'history_%d' % user_id
        sku_ids = redis_cli.lrange(history_key, 0, USER_BROWSING_HISTORY_COUNTS_LIMIT)
        return SKU.objects.filter(id__in=sku_ids)



















