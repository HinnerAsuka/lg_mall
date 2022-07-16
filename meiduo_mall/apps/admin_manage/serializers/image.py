from rest_framework import serializers
from apps.goods.models import SKUImage, SKU

class SKUImageModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKUImage
        fields = '__all__'


# 新增商品图片展示
class ShowSKUImageModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['id', 'name']