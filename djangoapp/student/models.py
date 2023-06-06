#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create your models here.

from datetime import datetime

from django.db import models

from ..common import T


class Clazz(models.Model, T):
    clazz_id = models.AutoField(primary_key=True)
    name = models.CharField('名称',max_length=50, null=False)
    description = models.CharField('描述',max_length=200, default='.')
    create_time = models.DateTimeField('创建时间',auto_now_add=True)

    class Meta:
        db_table = 'clazz'
        ordering = ['name']

    def __unicode__(self):
        return '%s' % self.name

    def __str__(self):
        return self.__unicode__()


class Student(models.Model, T):

    class Gender(models.IntegerChoices):
        """
        性别枚举
        """
        female = 0
        male = 1

    student_id = models.AutoField(primary_key=True)
    name = models.CharField('姓名', max_length=50, null=False)
    gender = models.IntegerField('性别', choices=Gender.choices, default=Gender.male)
    age = models.IntegerField('年龄', default=1)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    clazz = models.ForeignKey(Clazz, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'student'  # 定义表名
        ordering = ['-student_id']  # 按student_id倒序排序

    def __unicode__(self):
        return '%s' % self.name

    def __str__(self):
        return self.__unicode__()

    def to_dict(self):
        d = super(Student, self).to_dict()
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = '{v}'.format(v=v)
        return d
