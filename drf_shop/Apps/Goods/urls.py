from django.urls import path, include
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from .views import SKUListView, SKUSearchViewSet, GoodsDetailViewSet, GetUserHistoryView

router = DefaultRouter()
router.register('skus/search', SKUSearchViewSet, basename='skus_search')
router.register('detail', GoodsDetailViewSet, basename='detail')

urlpatterns = [
    # url('^categories/(?P<category_id>\d+)/skus/$', SKUListView.as_view()),
    path('categories/<category_id>/', SKUListView.as_view()),
    path('gethistory', GetUserHistoryView.as_view()),
    path(r'', include(router.urls)),
]