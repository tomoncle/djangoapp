#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create your models here.
from django.db import models


class Clazz(models.Model):
    clazz_id = models.AutoField(primary_key=True)  # pk
    name = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=200, default='.')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clazz'
        ordering = ['name']

    def __unicode__(self):
        return '%s' % self.name

    def __str__(self):
        return self.__unicode__()
