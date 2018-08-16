#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time           : 17-6-9 下午4:29
# @Author         : Tom.Lee
# @Description    :
# @File           : http_funcs.py
# @Product        : PyCharm


from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.http.request import QueryDict

__all__ = ['check_request_method', 'build_request_params', 'json_response', 'make_response']

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
                return HttpResponseNotAllowed(_HTTP_405)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def build_request_params():
    def decorator(func):
        def wrapper(*args, **kwargs):
            request = args[0]
            if request.method in ['GET', 'POST']:
                pass
            elif request.method == 'PUT':
                request.PUT = QueryDict(request.body)
            elif request.method == 'DELETE':
                request.DELETE = QueryDict(request.body)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def json_response():
    def decorator(func):
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            assert isinstance(res, (dict, list))
            return JsonResponse(res)

        return wrapper

    return decorator


def make_response(_object):
    def decorator(func):
        def wrapper(*args, **kwargs):
            request = args[0]
            call_func = getattr(_object(), '%s' % request.method.lower())
            return JsonResponse(call_func(*args,**kwargs))

        return wrapper

    return decorator
