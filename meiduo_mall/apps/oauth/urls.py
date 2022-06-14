from django.urls import path
from apps.oauth.views import QQLoginURLView, OauthQQ

urlpatterns = [
    path('qq/authorization/', QQLoginURLView.as_view(), name='qq_login'),
    path('oauth_callback/', OauthQQ.as_view(), name='qq_oauth'),
]