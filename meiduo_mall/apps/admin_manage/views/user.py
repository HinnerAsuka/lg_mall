from collections import OrderedDict
from apps.users.models import User
from rest_framework.views import APIView
from apps.admin_manage.serializers.user import UserSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# 分页
class PageNum(PageNumberPagination):
    page_size = 1
    # page_size_query_param = 'pagesize'
    max_page_size = 20

    # 重写源码，实现前端接收响应
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('lists', data),
            ('page', self.page.number),  # 第几页
            ('pages', self.page.paginator.num_pages),  # 总共几页
            # ('pagesize', self.page.paginator.per_page),     # 一页几条数据
            ('pagesize', self.page_size),  # 一页几条数据
        ]))


from rest_framework.generics import ListCreateAPIView


# 用户信息展示
class UserAPIView(ListCreateAPIView):
    # queryset = User.objects.all()
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')

        if keyword:
            return User.objects.filter(username__contains=keyword)

        return User.objects.all()

    serializer_class = UserSerializer
    pagination_class = PageNum
