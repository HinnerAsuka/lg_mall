from django.shortcuts import render

# Create your views here.

from django.views import View
from utils.goods import get_categories
from apps.contents.models import ContentCategory

# 商城首页
class IndexView(View):

    def get(self, request):
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
        return render(request, 'index.html', context)