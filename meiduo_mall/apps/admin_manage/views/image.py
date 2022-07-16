from apps.goods.models import SKUImage, SKU
from rest_framework.viewsets import ModelViewSet
from apps.admin_manage.serializers.image import SKUImageModelSerializer, ShowSKUImageModelSerializer
from apps.admin_manage.utils import PageNum


# 图片展示
class ImageModelViewSet(ModelViewSet):
    queryset = SKUImage.objects.all()
    serializer_class = SKUImageModelSerializer
    pagination_class = PageNum


from rest_framework.generics import ListAPIView


# 新增图片列表展示
class ImageSKUAPIView(ListAPIView):
    queryset = SKU.objects.all()
    serializer_class = ShowSKUImageModelSerializer