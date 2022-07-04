from django_redis import get_redis_connection
import base64
import pickle


# 将cookie中的购物车信息合并到redis中
def marge_cookie_to_redis(request, response):
    cookie_carts = request.COOKIES.get('carts')
    if cookie_carts:
        carts = pickle.loads(base64.b64decode(cookie_carts))
        # {sku_id: count}
        cookie_dict = {}
        selected_ids = []
        unselected_ids = []

        for sku_id, count_selected_dict in carts.items():
            cookie_dict[sku_id] = count_selected_dict['count']
            if count_selected_dict['selected']:
                selected_ids.append(sku_id)
            else:
                unselected_ids.append(sku_id)

        redis_cli = get_redis_connection('carts')
        pipeline = redis_cli.pipeline()
        pipeline.hmset(f'carts_{request.user.id}', cookie_dict)
        if len(selected_ids) > 0:
            # *selected 解包数据
            pipeline.sadd(f'selected_{request.user.id}', *selected_ids)
        if len(unselected_ids) > 0:
            pipeline.srem(f'selected_{request.user.id}', *unselected_ids)
        pipeline.execute()

        # 删除cookie
        response.delete_cookie('carts')

    return response
