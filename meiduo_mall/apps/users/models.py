from django.db import models

# Create your models here.

# django自带一个用户模型，这个用户模型有 密码加密和密码验证
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    mobile = models.CharField(max_length=11, verbose_name='手机号', unique=True)

    class Meta:
        db_table = 'lg_users'
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name