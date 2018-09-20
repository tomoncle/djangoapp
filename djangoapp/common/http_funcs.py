#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time           : 17-6-9 下午4:29
# @Author         : Tom.Lee
# @Description    :
# @File           : http_funcs.py
# @Product        : PyCharm

import time

from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.http.request import QueryDict

__all__ = [
    'check_request_method',
    'build_request_params',
    'json_response',
    'make_response'
]

_HTTP_405 = HttpResponse(405)


# from django.views.decorators.http import require_http_methods
# @require_http_methods(["POST"])
def check_request_method(method):
    def decorator(func):
        def wrapper(*args, **kwargs):
            request = args[0]
            # check_request_method: request method (request.method, method))
            if request.method not in method:
                # 不允许此方法
                # return HttpResponse(_HTTP_405)
                return HttpResponseNotAllowed(method)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def build_request_params(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        if request.method in ['GET', 'POST']:
            pass
        elif request.method == 'PUT':
            # mutable=True 表示可以修改
            request.PUT = QueryDict(request.body, mutable=True)
            if request.GET:
                request.PUT.update(request.GET)
        elif request.method == 'DELETE':
            # mutable=True 表示可以修改
            request.DELETE = QueryDict(request.body, mutable=True)
            if request.GET:
                request.DELETE.update(request.GET)
        elif request.method == 'PATCH':
            # mutable=True 表示可以修改
            request.PATCH = QueryDict(request.body, mutable=True)
            if request.GET:
                request.PATCH.update(request.GET)
        return func(*args, **kwargs)

    return wrapper


def json_response(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        assert isinstance(res, (dict, list))
        return JsonResponse(res)

    return wrapper


def make_response(_object):
    def decorator(func):
        def wrapper(*args, **kwargs):
            request = args[0]
            message = 'success'
            data = None
            try:
                call_func = getattr(_object(), '%s' % request.method.lower())
                data = call_func(*args, **kwargs)
                # if data and isinstance(data, dict):
                #     return JsonResponse(data)
                # return HttpResponse(data)
            except Exception as e:
                message = e

            status = message == 'success'
            return JsonResponse({
                'status': status,
                'timestamp': int(round(time.time() * 1000)),
                'data': data,
                'path': request.path,
                'method': request.method,
                'message': '{msg}'.format(msg=message or 'unknown')
            })

        return wrapper

    return decorator
