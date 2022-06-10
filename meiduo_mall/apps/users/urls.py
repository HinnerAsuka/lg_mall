from django.urls import path
from apps.users.views import UsernameCountView, RegisterView, MobileCountView

urlpatterns = [
    # 判断用户名,手机号是否存在
    path('usernames/<Username:username>/count', UsernameCountView.as_view(), name='username_count'),    # 使用自定义转换器Username
    path('mobiles/<Mobile:mobile>/count', MobileCountView.as_view(), name='mobile_count'),    # 使用自定义转换器Mobile

    # 注册功能
    path('register/', RegisterView.as_view(), name='register')
]
