#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/6 20:07
# @Author  : tomoncle
# @Site    : https://github.com/tomoncle
# @File    : urls.py
# @Software: PyCharm
from django.urls import path
from django.urls import re_path

from .views import StudentRestResponse, ClassRestResponse, student_index, students_list, student_save
from ..common import build_request_params
from ..common import check_request_method
from ..common import make_path_view
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


_student_url = [
    re_path('index', student_index),
    re_path('list', students_list),
    re_path('save', student_save),
    re_path(r'([0-9a-zA-Z]*)', student_handler),
]

_class_url = [
    re_path(r'([0-9a-zA-Z]*)', class_handler)
]

# application urls
student_patterns = [
    path('student/', make_path_view(_student_url, 'student')),
    path('class/', make_path_view(_class_url, 'class')),
]
