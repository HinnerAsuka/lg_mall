from django.urls import path
from apps.users.views import UsernameCountView, RegisterView, MobileCountView, LoginView, LogoutView, CenterView, EmailView, EmailVerifyView,\
    AddressCreateView, AddressView, AddressEditView, AddressDefaultView, AddressTitleView

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
    # 用户中心
    path('info/', CenterView.as_view(), name='info'),
    # 保存邮箱
    path('emails/', EmailView.as_view(), name='emails'),
    # 激活邮箱
    path('emails/verification/', EmailVerifyView.as_view(), name='emails_verify'),
    # 新增收货地址
    path('addresses/create/', AddressCreateView.as_view(), name='address_create'),
    # 地址展示
    path('addresses/', AddressView.as_view(), name='addresses'),
    # 修改收货地址和删除
    path('addresses/<id>/', AddressEditView.as_view(), name='address_edit'),
    # 设置默认地址
    path('addresses/<id>/default/', AddressDefaultView.as_view(), name='address_default'),
    # 修改地址标题
    path('addresses/<id>/title/', AddressTitleView.as_view()),
]
