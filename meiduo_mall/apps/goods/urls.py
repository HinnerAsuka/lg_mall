from django.urls import path
from apps.goods.views import IndexView, ListView, HotListView

urlpatterns = [
    # 商城首页
    path('index/', IndexView.as_view()),
    # 商品分类列表
    path('list/<category_id>/skus/', ListView.as_view()),
    # 热销商品列表
    path('hot/<category_id>/', HotListView.as_view())
]