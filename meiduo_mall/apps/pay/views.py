from django.shortcuts import render

# Create your views here.

from django.views import View
from apps.orders.models import OrderInfo
from django.http import JsonResponse
from utils.views import LoginRequiredJSONMixin
from meiduo_mall import settings
from alipay import AliPay, AliPayConfig

# 沙箱测试账号    wkqslg7343@sandbox.com  密码 111111 支付密码 111111

# 生成支付宝跳转链接
class PayUrlView(LoginRequiredJSONMixin, View):

    def get(self, request, order_id):
        user = request.user
        try:
            # 查询待支付的订单
            order = OrderInfo.objects.get(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'], user=user)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code': 400})

        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

        # 创建支付宝实例
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG,  # 默认False
            config=AliPayConfig(timeout=15)  # 可选, 请求超时时间
        )

        # 调用支付宝的支付方法
        # 如果你是 Python 3的用户，使用默认的字符串即可
        subject = "美多商城测试订单"

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # https://openapi.alipay.com/gateway.do 这个是线上的
        # 'https://openapi.alipaydev.com/gateway.do' 这个是沙箱的
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),  # 一定要进行类型转换,因为decimal不是基本数据类型
            subject=subject,
            return_url=settings.ALIPAY_RETURN_URL,  # 支付成功之后,跳转的页面
            notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
        )

        # 拼接连接
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        # 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'alipay_url': pay_url})

from apps.pay.models import Payment


class PaymentStatusView(View):

    def put(self, request):
        data = request.GET

        data = data.dict()
        signature = data.pop('sign')

        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG,  # 默认False
            config=AliPayConfig(timeout=15)  # 可选, 请求超时时间
        )
        success = alipay.verify(data, signature)
        if success:
            trade_no = data.get('trade_no')  # 支付宝交易号
            order_id = data.get('out_trade_no')  # 商家订单号
            Payment.objects.create(
                trade_id=trade_no,
                order_id=order_id
            )
            # 更新订单状态
            OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])
            return JsonResponse({'code': 0, 'trade_id': trade_no})
        else:
            return JsonResponse({'code': 400})