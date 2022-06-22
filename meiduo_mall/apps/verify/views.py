from django.shortcuts import render, HttpResponse
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http import JsonResponse
import random
import string
from libs.yuntongxun.sms import CCP


# Create your views here.


class ImageCodeView(View):

    def get(self, request, uuid):
        # 1. 接收路由中的 uuid
        # 2. 生成图片验证码和图片二进制
        # text 是图片验证码的内容 例如： xyzz
        # image 是图片二进制
        text, image = captcha.generate_captcha()

        # 3. 通过redis把图片验证码保存起来
        # 3.1 进行redis的连接
        redis_cli = get_redis_connection('code')
        # 3.2 指令操作
        # name, time, value
        redis_cli.setex('img_%s' % uuid, 100, text)
        # 4. 返回图片二进制
        # 因为图片是二进制 我们不能返回JSON数据
        # content_type=响应体数据类型
        # content_type 的语法形式是： 大类/小类
        # content_type (MIME类型)
        # 图片： image/jpeg , image/gif, image/png
        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):
    def get(self, request, mobile):
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 验证参数
        if not all([image_code, uuid]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        # 连接redis并用过uuid获取图片验证码
        redis_cli = get_redis_connection('code')
        redis_image_code = redis_cli.get('img_%s' % uuid)
        # 判断验证码是否过期
        if redis_image_code is None:
            return JsonResponse({'code': 400, 'errmsg': '图片验证码已过期'})

        # 判断用户输入的图片验证码是否正确
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': 400, 'errmsg': '图片验证码错误'})

        # 提取发送短信的标记
        sned_flag = redis_cli.get('send_flag_%s' % mobile)
        if sned_flag:
            return JsonResponse({'code': 400, 'errmsg': '请勿频繁发送短信'})

        # 生成短信验证码
        #方法一
        num = string.digits
        sms_code = "".join(random.sample(num, 6))
        # 方法二
        # sms_code = "%06d" % random.randint(0, 999999)

        # 管道技术-pipeline
        pipeline = redis_cli.pipeline()  # 新建管道
        pipeline.setex('sms_%s' % mobile, 300, sms_code)
        pipeline.setex('send_flag_%s' % mobile, 60, 1)
        pipeline.execute()

        # # 在redis中添加短信验证码
        # redis_cli.setex('sms_%s' % mobile, 300, sms_code)
        # # 在redis中添加一个发送标记
        # redis_cli.setex('send_flag_%s' % mobile, 60, 1)

        # 发送短信验证码
        # CCP().send_template_sms('15878761027', [sms_code, 5], 1)
        from celery_tasks.sms.tasks import celery_send_sms_code
        celery_send_sms_code.delay(mobile, sms_code)

        #  获取短信验证码参数
        sms_code = request.POST.get('sms_code')

        # 连接redis获取短信验证码
        redis_sms_code = redis_cli.get('sms_%s' % mobile)
        # 判断短信验证码是否过期
        if redis_sms_code is None:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码已过期'})

        # 判断输入的短信验证码与服务端存储的是否一致
        if redis_sms_code != sms_code.decode():
            return JsonResponse({'code': 400, 'errmsg': '短信验证码错误'})

        return JsonResponse({'code': 0, 'errmsg': 'ok'})