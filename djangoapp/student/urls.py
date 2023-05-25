#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/24 12:50
# @Author  : tomoncle
# @Site    : https://github.com/tomoncle/djangoapp
# @File    : urls.py
# @Software: PyCharm
from django.urls import re_path as url

from .views import student_handler

_student_urls = [url(r'([0-9a-zA-Z]*)$', student_handler)], 'student', 'student'

# application urls
student_patterns = [
    url(r'^student/', _student_urls),
]
