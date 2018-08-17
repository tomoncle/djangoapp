#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author         : Tom.Lee
import os
import time

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms import forms

from .http_funcs import json_response


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
    save_path = '/tmp/{name}'.format(name=object_file.name)
    if isinstance(object_file, InMemoryUploadedFile):
        # 假如是内存类型的文件，即是小文件,直接写入文件
        with open(save_path, 'wb') as desc:
            for chunk in object_file.chunks():
                desc.write(chunk)
    else:
        # 假如是大文件，直接rename, 即更新linux文件的inode
        os.rename(object_file.file.name, save_path)
    return {
        'status': True,
        'timestamp': int(round(time.time() * 1000)),
        'data': {
            'path': save_path,
            'size': object_file.size
        },
        'path': request.path,
        'method': request.method,
        'message': '文件"%s"上传成功！' % object_file.name
    }
