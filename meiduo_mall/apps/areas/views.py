from django.shortcuts import render

# Create your views here.
from django.views import View
from apps.areas.models import Area
from django.http import JsonResponse
from django.core.cache import cache

class AreaView(View):

    def get(self, request):
        # 先查询缓存数据
        province_list = cache.get('province')

        if province_list is None:
            provinces = Area.objects.filter(parent=None)  # 获取省的信息，得到结果是Queryset形式
            # 将对象数据转换为字典数据并存入列表中
            province_list = []
            for province in provinces:
                province_list.append({
                    'id': province.id,
                    'name': province.name,
                })

        # 保存缓存数据
        cache.set('province', province_list, 24 * 3600)  # 过期时间设置为一天

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'province_list': province_list})  # province_list 为前端js用到的名称


class SubAreaView(View):

    def get(self, request, id):
        data_list = cache.get('city:%s' % id)

        if data_list is None:
            # 上一级地区信息
            up_level = Area.objects.get(id=id)
            # 下一级地区信息
            down_level = up_level.subs.all()

            # 将对象数据转为字典数据
            data_list = []
            for item in down_level:
                data_list.append({
                    'id': item.id,
                    'name': item.name,
                })
        cache.set('city:%s' % id, data_list, 24 * 3600)
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'sub_data': {'subs': data_list}})