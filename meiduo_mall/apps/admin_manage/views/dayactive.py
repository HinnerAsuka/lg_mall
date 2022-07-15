from apps.users.models import User


# 日活用户统计

from datetime import date
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

class DailyActiveAPIView(APIView):

    def get(self, request):
        today = date.today()
        count = User.objects.filter(last_login__gte=today).count()
        return Response({'count': count})
