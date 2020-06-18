# @Time    : 2020/06/09
# @Author  : sunyingqiang
# @Email   :  344670075@qq.com
import os
import django
from django.core.mail import send_mail
from django.conf import settings
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_shop.settings')
django.setup()

app = Celery('celery_tasks.tasks', broker='redis://119.3.189.181:6379/5')

@app.task
def send_register_active_email(to_email, sms_code):
    """发送验证码"""
    subject = '验证码:'
    message = str(sms_code)
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    send_mail(subject, message, sender, receiver)
