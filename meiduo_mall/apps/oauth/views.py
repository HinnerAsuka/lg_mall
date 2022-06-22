import re

from django.shortcuts import render

# Create your views here.

from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall import settings
from django.http import JsonResponse
from apps.oauth.models import OAuthQQUser
from django.contrib.auth import login
import json
from django_redis import get_redis_connection
from apps.users.models import User
from authlib.jose import jwt, JoseError


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
            from apps.oauth.utils import generic_openid

            # 对openid进行加密
            access_token = generic_openid(openid)
            response = JsonResponse({'code': 400, 'access_token': access_token})  # 若没有绑定qq账号，前端需返回一个access_token，即openid
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

    def post(self, request):
        # 接收请求参数
        body_str = request.body
        body_dict = json.loads(body_str)

        # 获取请求参数
        mobile = body_dict.get('mobile')
        password = body_dict.get('password')
        sms_code = body_dict.get('sms_code')
        access_token = body_dict.get('access_token')

        # 添加对access_token的解密
        from apps.oauth.utils import check_access_token

        openid = check_access_token(access_token)
        if openid is None:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})

        # 验证请求参数
        if not all([mobile, password, sms_code, openid]):
            return JsonResponse({'coed': 400, 'errmsg': '参数不全'})
        if not re.match('1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': '手机号格式不正确'})
        if not re.match('^[a-zA-Z0-9_-]{8,20}$', password):
            return JsonResponse({'code': 400, 'errmsg': '请输入8-20位的密码'})

        redis_cli = get_redis_connection('code')
        redis_sms_code = redis_cli.get('sms_%s' % mobile)

        # 判断短信验证码是否失效
        if redis_sms_code is None:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码已失效'})
        if redis_sms_code != sms_code.encode():
            return JsonResponse({'code': 400, 'errmsg': '输入的验证码有误'})

        # if not openid:
        #     return JsonResponse({'code': 400, 'errmsg': '缺少openid'})

        # 根据手机号查询用户信息
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 手机号不存在
            # 创建一个新的用户
            user = User.objects.create_user(username=mobile, mobile=mobile, password=password)
        else:
            # 手机号存在
            if user.check_password(password) is False:
                return JsonResponse({'code': 400, 'errmsg': '账号或密码错误'})

        # 创建绑定的qq用户信息
        OAuthQQUser.objects.create(user=user, openid=openid)

        login(request, user)
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', user.username)
        return response