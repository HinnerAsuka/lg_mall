from django.shortcuts import render

# Create your views here.

from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall import settings
from django.http import JsonResponse
from apps.oauth.models import OAuthQQUser
from django.contrib.auth import login


# QQ登录链接
class QQLoginURLView(View):

    def get(self, request):
        qq = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state='xxx'
        )
        # 调用对象方法生成跳转链接
        qq_login_url = qq.get_qq_url()

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'login_url': qq_login_url})


class OauthQQ(View):

    def get(self, request):
        # 获取code
        code = request.GET.get('code')
        if code is None:
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        # 通过code获取token
        qq = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state='xxx'
        )
        token = qq.get_access_token(code)

        # 通过token换取openid
        openid = qq.get_open_id(token)

        # 根据openid进行查询判断
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # qq用户不存在
            response = JsonResponse({'code': 400, 'access_token': openid})  # 若没有绑定qq账号，前端需返回一个access_token，即openid
            return response
        else:
            # qq用户存在
            # 通过django自带的方法进行session设置
            login(request, qquser.user)
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            # 设置cookie
            response.set_cookie('username', qquser.user.username)
            return response
        pass
