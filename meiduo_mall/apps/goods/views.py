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


from utils.goods import get_breadcrumb
from apps.goods.models import GoodsCategory, SKU
from django.http import JsonResponse
from django.core.paginator import Paginator


# 商品列表页面
class ListView(View):

    def get(self, request, category_id):
        # 接收排序条件、
        ordering = request.GET.get('ordering')
        # 每页的数据量
        page_size = request.GET.get('page_size')
        # 要第几页的数据
        page = request.GET.get('page')

        # 获取分类id，根据分类id进行分类数据的查询与验证
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code': 0, 'errmsg': '参数不存在'})

        breadcrumb = get_breadcrumb(category)

        # 查询分类对应的sku数据，然后排序、分页
        sku = SKU.objects.filter(category=category, is_launched=True).order_by(ordering)

        paginater = Paginator(sku, page_size)

        # 获取指定页码数据
        page_skus = paginater.page(page)

        sku_list = []
        for sku in page_skus:
            sku_list.append(
                {
                    'id': sku.id,
                    'name': sku.name,
                    'price': sku.price,
                    'default_image_url': sku.default_image.url
                }
            )

        # 获取总页码
        total_pages = paginater.num_pages
        return JsonResponse(
            {'code': 0, 'errmsg': 'ok', 'list': sku_list, 'count': total_pages, 'breadcrumb': breadcrumb}
        )


# 热销商品页面
class HotListView(View):

    def get(self, request, category_id):

        skus = SKU.objects.filter(category_id=category_id, sales__gt=0)[0:2]
        hot_sku = []
        for sku in skus:
            hot_sku.append(
                {
                    'id': sku.id,
                    'name': sku.name,
                    'price': sku.price,
                    'default_image_url': sku.default_image.url
                }
            )

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'hot_skus': hot_sku})


from haystack.views import SearchView
# 搜索功能
class SKUSearchView(SearchView):

    def create_response(self):
        # 获取搜索结果
        context = self.get_context()

        sku_list = []
        for sku in context['page'].object_list:
            sku_list.append(
                {
                    'id': sku.object.id,
                    'name':sku.object.name,
                    'price': sku.object.price,
                    'default_image_url': sku.object.default_image.url,
                    'searchkey': context.get('query'),
                    'pagesize': context['page'].paginator.num_pages,
                    'count': context['page'].paginator.count
                }
            )
        return JsonResponse(sku_list, safe=False)

from utils.goods import get_goods_specs


# 商品详情
class DetailView(View):

    def get(self, request, sku_id):
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400})

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
        return render(request, 'detail.html', context)

from datetime import date
from apps.goods.models import GoodsVisitCount

class CategoryVisitCountView(View):

    def post(self, request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '分类不存在'})

        today = date.today()
        try:
            gvc = GoodsVisitCount.objects.get(category=category)
        except GoodsVisitCount.DoesNotExist:
            GoodsVisitCount.objects.create(category=category, date=today, count=1)
        else:
            gvc.count += 1
            gvc.save()
        return JsonResponse({'code': 0})