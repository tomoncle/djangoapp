#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/24 12:45
# @Author  : tomoncle
# @Site    : https://github.com/tomoncle/djangoapp
# @File    : urls.py
# @Software: PyCharm

from django.urls import re_path as url
from .views import sample


# application urls
sample_patterns = [
    url(r'^sample/$', sample),
]
