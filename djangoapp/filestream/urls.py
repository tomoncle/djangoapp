#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/24 13:05
# @Author  : tomoncle
# @Site    : https://github.com/tomoncle/djangoapp
# @File    : urls.py
# @Software: PyCharm

from django.urls import re_path as url

from . import download, download_large, download_proxy, upload

_urlpatterns = [
    url(r'^download/$', download),
    url(r'^dl_large/$', download_large),
    url(r'^dl_proxy/$', download_proxy),
    url(r'^upload/$', upload),
]

_file_stream_urls = _urlpatterns, 'file_stream', 'file_stream'

# application urls
file_patterns = [
    url(r'^files/', _file_stream_urls),
]
