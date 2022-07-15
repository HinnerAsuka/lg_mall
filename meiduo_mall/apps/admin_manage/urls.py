from django.urls import path
from apps.admin_manage.user import legou_jwt_token
from apps.admin_manage.views.dayactive import DailyActiveAPIView, DailyOrderAPIView, TotalUserAPIView,\
    DailyIncrementAPIView, MonthIncrementAPIView

urlpatterns = [
    path('authorizations/', legou_jwt_token),
    path('statistical/day_active/', DailyActiveAPIView.as_view()),
    path('statistical/day_orders/', DailyOrderAPIView.as_view()),
    path('statistical/total_count/', TotalUserAPIView.as_view()),
    path('statistical/day_increment/', DailyIncrementAPIView.as_view()),
    path('statistical/month_increment/', MonthIncrementAPIView.as_view()),
]