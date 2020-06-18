# @Time    : 2020/06/09
# @Author  : sunyingqiang
# @Email   :  344670075@qq.com
from django.db import models


class BaseModel(models.Model):
    """ 模型抽象基类"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        #指定是一个抽象基类
        abstract = True