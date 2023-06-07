from django.db import models

from ..common import T
import uuid


class Group(models.Model, T):
    group_id = models.AutoField(primary_key=True)
    name = models.CharField('名称', max_length=50, null=False)
    description = models.TextField('描述', default='默认主机组', null=True, blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        managed = True
        ordering = ['group_id']
        db_table = 't_webssh_group'
        verbose_name = '服务器组'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# Create your models here.
class Server(models.Model, T):

    class AuthType(models.IntegerChoices):
        """
        认证方式
        """
        PWD = 0, '密码'
        KEY = 1, '密钥'

    server_id = models.AutoField(primary_key=True)
    sid = models.UUIDField('UUID', default=uuid.uuid4, max_length=32)
    name = models.CharField('名称', max_length=50, null=False)
    auth = models.IntegerField('认证方式', choices=AuthType.choices, default=AuthType.PWD)
    host = models.CharField('IP', max_length=16, null=False, blank=False)
    port = models.IntegerField('端口', default=22)
    user = models.CharField('用户', max_length=50, default="root")
    password = models.CharField('密码', max_length=100, null=True, blank=True)
    secret_key = models.TextField('密钥', null=True, blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)

    class Meta:
        managed = True
        ordering = ['server_id']
        db_table = 't_webssh_server'
        verbose_name = '服务器'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
