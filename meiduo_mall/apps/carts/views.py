from django.shortcuts import render

# Create your views here.

from django.views import View
import json
from apps.goods.models import SKU
from django.http import JsonResponse
from django_redis import get_redis_connection
import base64
import pickle

class CartsView(View):

    def post(self, request):
        data = json.loads(request.body)
        # 获取数据
        sku_id = data.get('sku_id')
        count = data.get('count')
        # 验证数据
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '；商品不存在'})
        # 进行类型转换
        try:
            count = int(count)
        except Exception:
            count = 1

        user = request.user
        # 用户如果是认证用户（登录），进行redis操作
        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            # 用哈希格式保存
            # hset(key, field, value)
            redis_cli.hset(f'carts_{user.id}', sku_id, count)

            redis_cli.sadd(f'selected_{user.id}', sku_id)

            return JsonResponse({'code': 0})
        else:
            # 未登录进行cookie操作

            # 先读取cookie
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                # 解密
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                carts = {}

            if sku_id in carts:
                # 商品已存在购物车，进行累加
                origin_count = carts[sku_id]['count']   # 初始数量
                count += origin_count

            # 购物车中没有此商品
            carts[sku_id] = {
                'count': count,
                'selected': True
            }
            # 转为bytes类型
            carts_bytes = pickle.dumps(carts)
            # 加密
            base64_encode = base64.b64encode(carts_bytes)
            response = JsonResponse({'code': 0})
            response.set_cookie('carts', base64_encode.decode(), max_age=3600 * 24)
            return response


