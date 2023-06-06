#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/6 20:07
# @Author  : tomoncle
# @Site    : https://github.com/tomoncle
# @File    : urls.py
# @Software: PyCharm
from django.urls import path
from django.urls import re_path

from .views import StudentRestResponse,ClassRestResponse
from ..common import build_request_params
from ..common import check_request_method
from ..common import make_response


@check_request_method(["GET", "POST", "PUT", "DELETE", "HEAD", "PATCH"])
@build_request_params
@make_response(StudentRestResponse)
def student_handler(_request, *args, **kwargs):
    pass


@check_request_method(["GET", "POST", "PUT", "DELETE", "HEAD", "PATCH"])
@build_request_params
@make_response(ClassRestResponse)
def class_handler(_request, *args, **kwargs):
    pass


_student_url = [re_path(r'([0-9a-zA-Z]*)', student_handler)], 'student', 'student'
_class_url = [re_path(r'([0-9a-zA-Z]*)', class_handler)], 'class', 'class'

# application urls
student_patterns = [
    path('student/', _student_url),
    path('class/', _class_url),
]
