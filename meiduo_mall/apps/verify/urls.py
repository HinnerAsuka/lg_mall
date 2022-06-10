from django.urls import path
from apps.verify.views import ImageCodeView, SmsCodeView

urlpatterns = [
    path('image_codes/<uuid>/', ImageCodeView.as_view()),
    path('sms_codes/<Mobile:mobile>/', SmsCodeView.as_view()),
]