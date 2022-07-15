from apps.users.models import User
from datetime import date
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response


# 日活用户统计
class DailyActiveAPIView(APIView):

    def get(self, request):
        today = date.today()
        count = User.objects.filter(last_login__gte=today).count()
        return Response({'count': count})


# 日下单用户统计
class DailyOrderAPIView(APIView):

    def get(self, request):
        count = User.objects.filter(orderinfo__create_time__gte=date.today()).count()
        return Response({'count': count})


# 用户总量
class TotalUserAPIView(APIView):

    def get(self, request):
        count = User.objects.filter(is_active=1).count()
        return Response({'count': count})


# 日增用户
class DailyIncrementAPIView(APIView):

    def get(self, request):
        count = User.objects.filter(date_joined__gte=date.today()).count()
        return Response({'count': count})


from datetime import datetime


# 月增用户
class MonthIncrementAPIView(APIView):

    def get(self, request):
        count = User.objects.filter(date_joined__month=date.today().month).count()
        return Response({'count': count})
