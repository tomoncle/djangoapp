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
    from django.urls.resolvers import RegexURLPattern
    from django.http import JsonResponse

    def search_url(_urlpatterns, content_path, result=None):
        """
        获取URL
        :param _urlpatterns: 所有的 RegexURLResolver
        :param content_path: 根路径
        :param result: 当前的 RegexURLPattern 集合
        :return:
        """
        result = result or []
        for item in _urlpatterns:
            # 去掉url中的^和$
            url_path = item._regex.strip('^$')
            # 如果是RegexURLPattern直接追加
            if isinstance(item, RegexURLPattern):
                result.append(content_path + url_path)
            else:
                # 否则深度递归
                result.extend(search_url(item.urlconf_name, content_path + url_path))
        return result

    return JsonResponse({'paths': search_url(urlpatterns, '/')})


def page_not_found(request):
    """
    404 page config
    :param request:
    :return:
    """
    import json
    from django.shortcuts import render

    data = paths(request)
    data = data.content if data else b'{"paths": []}'
    return render(request, 'error/404.html', json.loads(data))
