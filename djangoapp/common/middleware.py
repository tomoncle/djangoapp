#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time           : 18-9-20 下午3:26
# @Author         : Tom.Lee
# @File           : middleware.py
# @Product        : PyCharm
# @Docs           : 
# @Source         : 
from django.utils.deprecation import MiddlewareMixin
from loguru import logger

from .common_funcs import ignore_self_waning


class GlobalRequestMiddleware(MiddlewareMixin):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    @ignore_self_waning
    def process_request(self, request):
        GlobalRequestMiddleware.__instance = request

    @classmethod
    def request(cls):
        return cls.__instance


class HttpMiddleware(MiddlewareMixin):
    """
    自定义一个 http 中间件
    """

    @ignore_self_waning
    def process_request(self, request):
        """处理每个请求"""
        content_type = request.headers.get('Content-Type') or ""
        request_data = 'Content-Type : [{}] data ignore.'.format(content_type)
        if 'application/json' in content_type:
            request_data = request.body.decode("utf-8")
        content = """监听请求信息:
Method   : {}
Header   : {}
Path     : {}
GET      : {}
Form     : {}
Body     : {}
Meta     : {}
""".format(request.method, request.headers, request.path, request.GET, request.POST, request_data, request.META)
        logger.trace(content)

    @ignore_self_waning
    def process_view(self, request, view_func, view_args, view_kwargs):
        """处理视图函数调用"""
        pass

    @ignore_self_waning
    def process_response(self, request, response):
        """处理每个响应"""
        content_type = response.headers.get('Content-Type')
        response_data = 'Content-Type : [{}] data ignore.'.format(content_type)
        if 'application/json' in content_type:
            response_data = response.content.decode("utf-8")
        content = """监听响应信息:
Method   : {}
Path     : {}
Response : {}
""".format(request.method, request.path, response_data)
        logger.trace(content)
        return response

    @ignore_self_waning
    def process_exception(self, request, exception):
        """处理视图异常"""
        # print('process_exception')
        pass
