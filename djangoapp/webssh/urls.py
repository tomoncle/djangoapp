#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/7 08:41
# @Author  : tomoncle
# @Site    : https://github.com/tomoncle
# @File    : urls.py
# @Software: PyCharm

from django.urls import path

from . import ssh
from . import tests
from . import views

websocket_patterns = [
    # websocket 配置
    path('webssh/ws/terminal/', ssh.SSHConsumer.as_asgi()),
    path('webssh/terminal/', ssh.SSHWebSocket.as_asgi())
]

webssh_patterns = [
    path('webssh/test1/', tests.test1),
    path('webssh/test2/', tests.test2),
    path('webssh/test3/', tests.test3),
    path('webssh/test4/', tests.test4),
    #
    path('webssh/index/', views.index)
]
