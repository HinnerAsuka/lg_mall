from django.urls import path
from apps.users.views import UsernameCountView, RegisterView

urlpatterns = [
    # 判断用户名是否存在
    # 使用自定义转换器Username
    path('usernames/<Username:username>/count', UsernameCountView.as_view(), name='username_count'),
    path('register/', RegisterView.as_view(), name='register')
]
