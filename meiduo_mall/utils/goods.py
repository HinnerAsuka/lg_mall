from apps.goods.models import GoodsChannel, GoodsCategory
from collections import OrderedDict

def get_categories():
    # 定义一个有序字典对象
    categories = OrderedDict()

    channels = GoodsChannel.objects.order_by('group_id', 'sequence')    # 对商品频道进行 group_id 和 sequence 排序

    # 遍历排序后的结果，得到所有一级菜单(频道)
    for channel in channels:
        # 从频道得到当前的组id
        group_id = channel.group_id

        # 如果当前组id不在有序字典中
        if group_id not in categories:
            # 就将组id添加到有序字典中
            categories[group_id] = {
                'channels': [],
                'sub_cats': []
            }

        # 获取当前频道的分类名称
        cat1 = channel.category
        categories[group_id]['channels'].append(
            {
                'id': cat1.id,
                'name': cat1.name,
                'url': channel.url
            }
        )

        # 获取当前类别的子类别,二级菜单
        cat2s = GoodsCategory.objects.filter(parent=cat1)
        for cat2 in cat2s:
            cat2.sub_cats = []

            # 获取三级菜单
            cat3s = GoodsCategory.objects.filter(parent=cat2)
            for cat3 in cat3s:
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)

    return categories