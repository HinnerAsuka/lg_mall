from django.urls import path
from apps.users.views import UsernameCountView, RegisterView, MobileCountView, LoginView, LogoutView, CenterView

urlpatterns = [
    # 判断用户名,手机号是否存在
    path('usernames/<Username:username>/count', UsernameCountView.as_view(), name='username_count'),    # 使用自定义转换器Username
    path('mobiles/<Mobile:mobile>/count', MobileCountView.as_view(), name='mobile_count'),    # 使用自定义转换器Mobile
    # 注册功能
    path('register/', RegisterView.as_view(), name='register'),
    # 登陆功能
    path('login/', LoginView.as_view(), name='login'),
    # 退出功能
    path('logout/', LogoutView.as_view(), name='logout'),
    # 用户未登陆返回JSON数据
    path('center/', CenterView.as_view(), name='center'),
]
