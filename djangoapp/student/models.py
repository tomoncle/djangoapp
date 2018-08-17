#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create your models here.

from datetime import datetime

from django.db import models

from ..clazz.models import Clazz
from ..common import T


class Student(models.Model, T):
    student_id = models.AutoField(primary_key=True)  # pk
    name = models.CharField(max_length=50, null=False)
    age = models.IntegerField(default=1)
    create_time = models.DateTimeField(auto_now_add=True)
    clazz = models.ForeignKey(Clazz, null=True)

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
