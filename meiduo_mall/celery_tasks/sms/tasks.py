
# 生产者
# 这个函数必须让Celery的实例的 task 装饰器进行装饰
from libs.yuntongxun.sms import CCP
from celery_tasks.main import app

@app.task
def celery_send_sms_code(mobile, code):

    CCP().send_template_sms(mobile, [code, 5], 1)
