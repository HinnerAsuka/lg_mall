from collections import OrderedDict

# 分页
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageNum(PageNumberPagination):
    page_size = 10
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