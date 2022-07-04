from django.shortcuts import render

# Create your views here.

from django.views import View
from utils.views import LoginRequiredJSONMixin
from apps.users.models import Address
from django_redis import get_redis_connection
from apps.goods.models import SKU
from django.http import JsonResponse

# 提交订单页面展示
class OrderSettlementView(LoginRequiredJSONMixin, View):

    def get(self, request):
        user = request.user
        addresses = Address.objects.filter(is_deleted=False)
        address_list = []
        for address in addresses:
            address_list.append(
                {
                    'id': address.id,
                    'province': address.province.name,
                    'cit': address.city.name,
                    'district': address.district.name,
                    'place': address.place,
                    'receiver': address.receiver,
                    'mobile': address.mobile
                }
            )

        # 获取购物车信息
        redis_cli = get_redis_connection('carts')
        pipeline = redis_cli.pipeline()
        pipeline.hgetall(f'carts_{user.id}')
        pipeline.smembers(f'selected_{user.id}')
        result = pipeline.execute()
        sku_id_counts = result[0]
        selected_ids = result[1]

        selected_carts = {}
        for sku_id in selected_ids:
                selected_carts[int(sku_id)] = int(sku_id_counts[sku_id])

        sku_list = []
        for sku_id, count in selected_carts.items():
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(
                {
                    'id': sku.id,
                    'name': sku.name,
                    'price': sku.price,
                    'default_image_url': sku.default_image.url,
                    'count': count
                }
            )

        from decimal import Decimal

        freight = Decimal('10')  # decimal 货币类型
        context = {
            'skus': sku_list,
            'addresses': address_list,
            'freight': freight
        }
        return JsonResponse({'code': 0, 'context': context})