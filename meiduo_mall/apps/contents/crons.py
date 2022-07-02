from django.template import loader
import os
from meiduo_mall import settings
from utils.goods import get_categories
from apps.contents.models import ContentCategory
import time


def generic_index():
    print('========%s========' % time.ctime())
    # 获取分类数据
    categories = get_categories()

    # 广告数据
    contents = {}
    content_categories = ContentCategory.objects.all()
    for content in content_categories:
        contents[content.key] = content.content_set.filter(status=True).order_by('sequence')

    context = {
        'categories': categories,
        'contents': contents
    }
    index_template = loader.get_template('index.html')
    index_html = index_template.render(context)
    file = os.path.join(os.path.dirname(settings.BASE_DIR), 'front_end_pc/index.html')
    with open(file, 'w') as f:
        f.write(index_html)
    f.close()