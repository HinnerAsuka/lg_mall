from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings')

# 实例化Celery
# 参数1:main 设置为脚本路径
app = Celery('celery_tasks')

# 设置broker，通过加载配置文件设置
app.config_from_object('celery_tasks.config')

# 让celery自动检测包，参数为列表
app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
