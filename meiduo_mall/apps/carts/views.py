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
            # redis_cli.hset(f'carts_{user.id}', sku_id, count)

            # 通过管道获取数据
            pipeline = redis_cli.pipeline()

            # hincrby会进行累加操作
            pipeline.hincrby(f'carts_{user.id}', sku_id, count)
            # 用集合保存选中商品
            pipeline.sadd(f'selected_{user.id}', sku_id)
            pipeline.execute()  # 执行管道
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

    # 购物车的展示
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            # 已登录操作redis
            redis_cli = get_redis_connection('carts')
            sku_id_count = redis_cli.hgetall(f'carts_{user.id}')
            selected_ids = redis_cli.smembers(f'selected_{user.id}')

            # 将redis数据转换为和cookie一样的数据
            carts = {}
            for sku_id, count in sku_id_count.items():
                carts[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in selected_ids
                }
        else:
            # 未登录操作cookie
            # 先读取cookie
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                # 解密
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                carts = {}

        sku_ids = carts.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        sku_list = []
        for sku in skus:
            sku_list.append(
                {
                    'id': sku.id,
                    'name': sku.name,
                    'price': sku.price,
                    'default_image_url': sku.default_image.url,
                    'selected': carts[sku.id]['selected'],  # 选中状态
                    'count': int(carts[sku.id]['count']),    # 数量
                    'amount': sku.price * carts[sku.id]['count']    # 总价格
                }
            )
        return JsonResponse({'code': 0, 'cart_skus': sku_list})

    # 修改购物车数据
    def put(self, request):
        user = request.user
        data = json.loads(request.body)

        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected')

        if not all([sku_id, count]):
            return JsonResponse({'code': 400})

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400})

        try:
            count = int(count)
        except:
            count = 1

        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            pipeline = redis_cli.pipeline()
            pipeline.hset(f'carts_{user.id}', sku_id, user.id)

            if selected:    # selected状态为True
                pipeline.sadd(f'selected_{user.id}', sku_id)
            else:
                pipeline.srem(f'selected_{user.id}', sku_id)
            pipeline.execute()

            return JsonResponse({'code': 0, 'cart_sku': {'count': count, 'selected': selected}})
        else:
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                # 解密
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                carts = {}
            if sku_id in carts:
                carts[sku_id] = {
                    'count': count,
                    'selected': selected
                }

            new_carts = base64.b64encode(pickle.dumps(carts))
            response = JsonResponse({'code': 0, 'cart_sku': {'count': count, 'selected': selected}})
            response.set_cookie('carts', new_carts.decode(), max_age=3600 * 24)
            return response

    # 删除购物车数据
    def delete(self, request):
        data = json.loads(request.body)
        sku_id = data.get('sku_id')

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400})

        user = request.user
        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            redis_cli.hdel(f'carts_{user.id}', sku_id)
            redis_cli.srem(f'selected_{user.id}', sku_id)

            return JsonResponse({'code': 0})
        else:
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                # 解密
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                carts = {}

            del carts[sku_id]
            new_carts = base64.b64encode(pickle.dumps(carts))
            response = JsonResponse({'code': 0})
            response.set_cookie('carts', new_carts.decode(), max_age=3600 * 24)
            return response