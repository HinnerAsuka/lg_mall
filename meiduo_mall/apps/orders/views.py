import json

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


from apps.orders.models import OrderInfo, OrderGoods
from django.utils import timezone
from decimal import Decimal
from django.db import transaction


# 提交订单功能
class OrderCommitView(View):

    def post(self, request):
        user = request.user
        data = json.loads(request.body)
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')

        if not all([address_id, pay_method]):
            return JsonResponse({'code': 400})

        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code': 400})

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return JsonResponse({'code': 400})

        # 生成订单id    年月日时分秒 + 用户id(要求为9位)
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + '%09d' % user.id

        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            pay_status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            pay_status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        total_count = 0  # 商品数量
        total_amount = Decimal('0')  # 总金额
        freight = Decimal('10.00')  # 运费

        # 事务
        with transaction.atomic():

            point = transaction.savepoint()  # 事务开始点

            orderinfo = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                total_count=total_count,
                total_amount=total_amount + freight,
                freight=freight,
                pay_method=pay_method,
                status=pay_status,
                address=address
            )

            redis_cli = get_redis_connection('carts')
            sku_id_counts = redis_cli.hgetall(f'carts_{user.id}')
            selected_ids = redis_cli.smembers(f'selected_{user.id}')
            carts = {}
            for sku_id in selected_ids:
                carts[int(sku_id)] = int(sku_id_counts[sku_id])  # 获取商品对应的数量

            for sku_id, count in carts.items():
                sku = SKU.objects.get(id=sku_id)
                if sku.stock < count:  # 如果库存小于购买数量，则说明库存不足

                    transaction.savepoint_rollback(point)   # 回滚点(回到开始点)
                    return JsonResponse({'code': 400, 'errmsg': '库存不足'})

                sku.stock -= count  # 减少库存
                sku.sales += count  # 增加销量
                sku.save()

                orderinfo.total_count += count  # 订单里商品的总量
                orderinfo.total_amount += (count * sku.price)  # 订单里商品的总价

                OrderGoods.objects.create(
                    order=orderinfo,
                    count=count,
                    sku=sku,
                    price=sku.price
                )
            orderinfo.save()
            transaction.savepoint_commit(point)   # 事务提交点
        return JsonResponse({'code': 0, 'order_id': order_id})
