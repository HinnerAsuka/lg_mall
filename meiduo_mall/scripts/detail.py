#!/usr/bin/env python

# ../ 为上一级目录，也就三base_dir
import sys
sys.path.insert(0, '../')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings')

import django
django.setup()


from utils.goods import get_categories, get_goods_specs, get_breadcrumb
from apps.goods.models import SKU
from django.template import loader
from meiduo_mall import settings


def generic_detail(sku):
    # 分类数据
    categories = get_categories()
    # 面包屑
    breadcrumb = get_breadcrumb(sku.category)
    # 商品规格信息
    goods_specs = get_goods_specs(sku)

    context = {
        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'goods_specs': goods_specs
    }

    # 加载模板
    detail_template = loader.get_template('detail.html')
    # 模板渲染
    detail_html = detail_template.render(context)
    # 写入到指定文件
    file = os.path.join(os.path.dirname(settings.BASE_DIR), 'front_end_pc/goods/%s.html' % sku.id)
    with open(file, 'w') as f:
        f.write(detail_html)
    f.close()

if __name__ == '__main__':
    skus = SKU.objects.all()
    for sku in skus:
        generic_detail(sku)