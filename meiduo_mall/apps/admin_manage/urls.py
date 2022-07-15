from django.urls import path
from apps.admin_manage.user import legou_jwt_token
from apps.admin_manage.views.dayactive import DailyActiveAPIView

urlpatterns = [
    path('authorizations/', legou_jwt_token),
    path('statistical/day_active/', DailyActiveAPIView.as_view()),
]