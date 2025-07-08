#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create your views here.
from django.http import JsonResponse

from ..common import route
from ..common import route_class


@route_class
class DemoController:
    @route('/demo/', methods=['GET'])
    def list_users(self, request):
        from ..common.django_tools import get_all_urls

        return JsonResponse({'users': get_all_urls()})

    @route('/demo/<int:user_id>/', methods=['GET'])
    def get_user(self, request, user_id):
        return JsonResponse({'user_id': user_id})


# 使用前缀
@route_class(prefix='/demo/v1')
class ApiController:
    @route('/users/', methods=['POST'])  # 实际路由: /api/v1/users/
    def list_users(self, request):
        return JsonResponse({'users': []})

    @route('/products/', methods=['PUT'])  # 实际路由: /api/v1/products/
    def list_products(self, request):
        return JsonResponse({'products': []})
