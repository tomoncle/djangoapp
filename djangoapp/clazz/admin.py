#!/usr/bin/env python
# -*- coding: utf-8 -*-
# docs : https://docs.djangoproject.com/en/1.10/ref/


from django.contrib import admin

from .models import Clazz


@admin.register(Clazz)
class ClazzAdmin(admin.ModelAdmin):
    list_display = ('clazz_id', 'name', 'description', 'create_time')  # 显示属性并排序
    list_filter = ('create_time',)  # 查询条件

# Register your models here.
# admin.site.register(Clazz, ClazzAdmin)
