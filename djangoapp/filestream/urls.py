#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/24 13:05
# @Author  : tomoncle
# @Site    : https://github.com/tomoncle/djangoapp
# @File    : urls.py
# @Software: PyCharm

from django.urls import re_path, path

from . import download, download_large, download_proxy, upload

_urlpatterns = [
    re_path(r'download/', download),
    re_path(r'download_large/', download_large),
    re_path(r'download_proxy/', download_proxy),
    re_path(r'upload/', upload),
]

_file_stream_urls = _urlpatterns, 'file_stream', 'file_stream'

# application urls
file_patterns = [
    path('files/', _file_stream_urls),
]
