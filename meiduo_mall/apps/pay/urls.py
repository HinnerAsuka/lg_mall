from django.urls import path
from apps.pay.views import PayUrlView


urlpatterns = [
    path('payment/<order_id>/', PayUrlView.as_view()),
]