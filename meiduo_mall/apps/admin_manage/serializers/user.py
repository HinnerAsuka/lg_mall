from rest_framework import serializers
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mobile', 'password']


    # 重写创建方法，实现对密码的加密
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)