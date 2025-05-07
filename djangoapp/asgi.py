"""
ASGI config for djangoapp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/


################### 使用ASGI运行Django ###################
1. 安装 Daphne
python -m pip install daphne

2. 使用 Daphne 启动 Django
daphne djangoapp.asgi:application

#################### 集成 runserver #####################
Daphne 提供了一个 runserver 命令，可以在开发期间在 ASGI 下为您的站点提供服务。
这可以通过将 daphne 添加到 INSTALLED_APPS 的开头，并添加指向 ASGI 应用程序对象的 ASGI_APPLICATION 设置来启用：

INSTALLED_APPS = [
    "daphne",
    ...,
]

ASGI_APPLICATION = "djangoapp.asgi.application"

运行：python manager.py runserver
"""

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoapp.settings')
django.setup()
# 注意：django.setup()要置顶，不能在底部，否则使用 daphne djangoapp.asgi:application 启动会出现下面的错误:
#
# django.core.exceptions.ImproperlyConfigured: Requested setting DEFAULT_CHARSET, but settings are not configured.
# You must either define the environment variable DJANGO_SETTINGS_MODULE or
# call settings.configure() before accessing settings.


from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from djangoapp.webssh.urls import websocket_patterns

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoapp.settings')

# application = get_asgi_application()

# 使用 ASGI 支持 websocket 和 http
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(URLRouter(websocket_patterns)),
})
