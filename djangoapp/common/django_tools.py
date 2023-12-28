#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author         : Tom.Lee
import platform
import time

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms import forms

from .file_tools import copy_file
from .file_tools import rename_file
from .http_funcs import json_response
from ..settings import UPLOAD_DIR


class UploadObjectForm(forms.Form):
    """
    docs: https://github.com/amlyj/horizon/blob/master/openstack_dashboard/api/rest/swift.py

    使用方法：
        form = UploadObjectForm(request.POST, request.FILES)
        if not form.is_valid():
            print '数据不能为空'
        data = form.clean()
        object_file = data['file']
        print 'file_name: %s' % object_file.name
        print 'file_size: %s' % object_file.size
    """
    file = forms.FileField(required=False)


@json_response
def save_file(request):
    form = UploadObjectForm(request.POST, request.FILES)
    if not form.is_valid():
        return {
            'status': False,
            'timestamp': int(round(time.time() * 1000)),
            'data': None,
            'path': request.path,
            'method': request.method,
            'message': '上传失败！ 文件不能为空.'
        }
    data = form.clean()
    object_file = data['file']
    # print('file_name: %s' % object_file.name)
    # print('file_size: %s' % object_file.size)
    save_path = '{upload_dir}/{name}'.format(upload_dir=UPLOAD_DIR, name=object_file.name)
    if isinstance(object_file, InMemoryUploadedFile):
        # 假如是内存类型的文件，即是小文件,直接写入文件
        with open(save_path, 'wb') as desc:
            for chunk in object_file.chunks():
                desc.write(chunk)
    else:
        # 假如是大文件，系统默认直接rename, 即更新linux文件的inode
        _func = rename_file
        # window环境使用copyfile, rename 会有权限问题
        if platform.system() == 'Windows':
            _func = copy_file
        _func(object_file.file.name, save_path)

    return {
        'status': True,
        'timestamp': int(round(time.time() * 1000)),
        'data': {
            'path': save_path,
            'size': object_file.size
        },
        'path': request.path,
        'method': request.method,
        'message': '文件 [%s] 上传成功！' % object_file.name
    }


def paths(request):
    """
    获取 项目所有的URL信息
    :param request:
    :return:
    """
    from ..urls import urlpatterns
    #  django 1.x
    # from django.urls.resolvers import RegexURLPattern
    # django 2.x +
    from django.urls import URLPattern, URLResolver
    from django.http import JsonResponse

    for u in urlpatterns:
        print()
        if isinstance(u, URLResolver):
            print(u, u.pattern, u.url_patterns)
        if isinstance(u, URLPattern):
            print(u, u.pattern)

    return JsonResponse({'paths': ""})


def page_not_found(request, e):
    """
    404 page config
    :param request:
    :param e : exception
    :return:
    """
    from django.shortcuts import render
    if e:
        print("404 异常：", e)
    return render(request, 'error/404.html')


def make_path_view(urlconf, app_name, namespace=None):
    """
    构建 from django.urls import path 函数中的 view 变量
    .
    :param urlconf: re_path 列表 [re_path('index', student_index), re_path(r'([0-9a-zA-Z]*)', student_handler),]
    :param app_name: 应用名称
    :param namespace: 应用所在模块
    :return: tuple
    """
    return urlconf, app_name, namespace or app_name
