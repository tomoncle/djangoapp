#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WSGI config for djangoapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
https://docs.djangoproject.com/zh-hans/4.2/howto/deployment/wsgi/

# 1.安装 gunicorn
pip install gunicorn

# 2.使用 wsgi 需要将当前项目加入 PYTHONPATH 环境变量
$ export PYTHONPATH=$PYTHONPATH:`pip -V | awk '{print $4}' | awk '{gsub(/\/pip/,"");print}'`:`pwd`
$ export PYTHONPATH=$PYTHONPATH:/root/.local/share/virtualenvs/djangoapp-yg1Eq-7T/lib/python3.9/site-packages:/opt/djangoapp

# 3.启动
$ gunicorn djangoapp.wsgi
[2023-05-25 08:34:14 +0000] [7556] [INFO] Starting gunicorn 20.1.0
[2023-05-25 08:34:14 +0000] [7556] [INFO] Listening at: http://127.0.0.1:8000 (7556)
[2023-05-25 08:34:14 +0000] [7556] [INFO] Using worker: sync
[2023-05-25 08:34:14 +0000] [7557] [INFO] Booting worker with pid: 7557

# 4.使用gevent 进行异步处理
$ gunicorn -k gevent djangoapp.wsgi
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoapp.settings')

application = get_wsgi_application()
