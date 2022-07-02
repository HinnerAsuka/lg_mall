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


# 面包屑
def get_breadcrumb(category):

    dict = {
        'cat1': '',
        'cat2': '',
        'cat3': '',
    }
    if category.parent is None:
        dict['cat1'] = category.name
    elif category.parent.parent is None:
        dict['cat1'] = category.parent.name
        dict['cat2'] = category.name
    else:
        dict['cat1'] = category.parent.parent.name
        dict['cat3'] = category.parent.name
        dict['cat2'] = category.name

    return dict

"""
规格选项
"""
def get_goods_specs(sku):
    # 构建当前商品的规格键
    sku_specs = sku.specs.order_by('spec_id')
    sku_key = []
    for spec in sku_specs:
        sku_key.append(spec.option.id)

    # 获取当前商品的所有SKU
    skus = sku.spu.sku_set.all()
    # 构建不同规格参数（选项）的sku字典
    spec_sku_map = {}
    for s in skus:
        # 获取sku的规格参数
        s_specs = s.specs.order_by('spec_id')
        # 用于形成规格参数-sku字典的键
        key = []
        for spec in s_specs:
            key.append(spec.option.id)
        # 向规格参数-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id

    # 以下代码为：在每个选项上绑定对应的sku_id值
    # 获取当前商品的规格信息
    goods_specs = sku.spu.specs.order_by('id')
    # 若当前sku的规格信息不完整，则不再继续
    if len(sku_key) < len(goods_specs):
        return
    for index, spec in enumerate(goods_specs):
        # 复制当前sku的规格键
        key = sku_key[:]
        # 该规格的选项
        spec_options = spec.options.all()
        for option in spec_options:
            # 在规格参数sku字典中查找符合当前规格的sku
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))
        spec.spec_options = spec_options

    return goods_specs

