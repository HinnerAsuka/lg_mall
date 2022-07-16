from django.urls import path
from apps.admin_manage.user import legou_jwt_token
from apps.admin_manage.views.dayactive import DailyActiveAPIView, DailyOrderAPIView, TotalUserAPIView,\
    DailyIncrementAPIView, MonthIncrementAPIView
from apps.admin_manage.views.user import UserAPIView
from apps.admin_manage.views.image import ImageSKUAPIView


urlpatterns = [
    path('authorizations/', legou_jwt_token),
    path('statistical/day_active/', DailyActiveAPIView.as_view()),
    path('statistical/day_orders/', DailyOrderAPIView.as_view()),
    path('statistical/total_count/', TotalUserAPIView.as_view()),
    path('statistical/day_increment/', DailyIncrementAPIView.as_view()),
    path('statistical/month_increment/', MonthIncrementAPIView.as_view()),
    path('users/', UserAPIView.as_view()),
    # 新增图片列表展示
    path('skus/simple/', ImageSKUAPIView.as_view()),
]

from rest_framework.routers import DefaultRouter
from apps.admin_manage.views.image import ImageModelViewSet

router = DefaultRouter()
router.register('skus/images', ImageModelViewSet, basename='images')
urlpatterns += router.urls