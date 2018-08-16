#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url

from ..common import build_request_params
from ..common import check_request_method
from ..common import make_response


# Create your views here.
class RestResponse(object):
    """
    views.func 函数中传入多少参数，method要传入对应数量的参数
    """

    def post(self, _request, *args):
        """
        http://localhost:8000/rest/request/
        :param _request:
        :param args:
        :return:
        """
        params = _request.POST
        return {'code': 200, 'params': params, 'method': 'post'}

    def get(self, _request, get_id=None):
        """
        http://localhost:8000/rest/request/1?username=tom
        http://localhost:8000/rest/request?username=tom
        :param _request:
        :param get_id:
        :return:
        """
        params = _request.GET
        if get_id:
            return {'code': 200, 'params': params, 'method': 'get', 'path': get_id}
        return {'code': 200, 'params': params, 'method': 'get'}

    def put(self, _request, *args):
        """
        http://localhost:8000/rest/request/
        :param _request:
        :param args:
        :return:
        """
        params = _request.PUT
        return {'code': 200, 'params': params, 'method': 'put'}

    def delete(self, _request, del_id):
        """
        http://localhost:8000/rest/request/1
        :param _request:
        :param del_id:
        :return:
        """
        return {'code': 200, 'params': del_id, 'method': 'delete'}

    def head(self, _request, *args):
        """
        http://localhost:8000/rest/request/
        :param _request:
        :param args:
        :return:
        """
        return {'code': 200, 'data': 'hello world', 'method': 'head'}

    def patch(self, _request, *args):
        """
        http://localhost:8000/rest/request/
        :param _request:
        :param args:
        :return:
        """
        return {'code': 200, 'data': 'hello world', 'method': 'patch'}


@check_request_method(["GET", "POST", "PUT", "DELETE", "HEAD", "PATCH"])
@build_request_params()
@make_response(RestResponse)
def student(_request, *args, **kwargs):
    pass


urls = [url(r'([0-9a-zA-Z]*)$', student)], 'student', 'student'
