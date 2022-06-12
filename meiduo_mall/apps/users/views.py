import json
import re
from django.shortcuts import render

# Create your views here.

"""
判断用户名是否重复的功能。

前端(了解)：     当用户输入用户名之后，失去焦点， 发送一个axios(ajax)请求

后端（思路）：
    请求:         接收用户名 
    业务逻辑：     
                    根据用户名查询数据库，如果查询结果数量等于0，说明没有注册
                    如果查询结果数量等于1，说明有注册
    响应          JSON 
                {code:0,count:0/1,errmsg:ok}

    路由      GET         usernames/<username>/count/        
   步骤：
        1.  接收用户名
        2.  根据用户名查询数据库
        3.  返回响应         

"""

from django.views import View
from apps.users.models import User
from django.http import JsonResponse
from django.contrib.auth import login


# 判断用户名是否重复
class UsernameCountView(View):
    def get(self, request, username):
        # 接收用户名,判断是否符合标准
        # if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
        #     return JsonResponse({'code': 200, 'errmsg': '用户名不符合要求'})

        # 根据用户名查询数据库
        count = User.objects.filter(username=username).count()
        return JsonResponse({"code": 0, "count": count, 'errmsg': 'ok'})


# 判断手机号是否重复
class MobileCountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code': 0, 'count': count, 'errmsg': 'ok'})


# 注册功能
class RegisterView(View):
    def post(self, request):
        body_str = request.body
        body_dict = json.loads(body_str)

        # 获取数据
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow = body_dict.get('allow')

        # 验证数据
        # 判断参数是否存在
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        # 判断各个参数是否符合要求
        if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
            return JsonResponse({'code': 400, 'errmsg': '用户名不符合要求'})

        if not re.match('^[a-zA-Z0-9_-]{8,20}$', password):
            return JsonResponse({'code': 400, 'errmsg': '密码不符合要求'})

        if not re.match('^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': '请输入正确的手机号'})

        # user = User(username=username, password=password, mobile=mobile)
        # user.save()

        # 对密码进行加密
        user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 状态保持
        login(request, user)
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


# 登陆功能
class LoginView(View):
    def post(self, request):
        # 获取用户登陆的json数据
        body_str = request.body
        # 解析json数据转换为字典格式
        body_dict = json.loads(body_str)

        # 接收数据
        username = body_dict.get('username')
        password = body_dict.get('password')
        remembered = body_dict.get('remembered')

        # 验证数据
        if not all([username, password]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        # 使用系统提供的验证用户信息方法
        from django.contrib.auth import authenticate

        # 判断用户输入的是手机号还是用户名
        if re.match('1[3-9]\d{9}$', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

        # 若用户名密码不正确，返回None
        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse({'code': 400, 'errmsg': '账号或密码错误'})

        # session状态保持
        login(request, user)

        # 判断是否记住登陆
        if remembered is True:
            request.session.set_expiry(60 * 60 * 24 * 7)    # 设置session存在时间：一周， None参数默认时间为两周
        else:
            # 不记住密码
            request.session.set_expiry(0)   # 参数为0，关闭浏览器就过期

        # 给返回的json数据中添加cookie信息
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', username, max_age=60 * 60 * 24 * 7)     # 为了首页显示用户信息

        return response


# 退出功能
from django.contrib.auth import logout


class LogoutView(View):
    def delete(self, request):
        logout(request)
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')
        return response


# 用户未登陆的话，用户中心返回JSON数据
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.views import LoginRequiredJSONMixin


class CenterView(LoginRequiredJSONMixin, View):
    def get(self, request):
        return JsonResponse({'code': 0, 'errmsg': 'ok'})