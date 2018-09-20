#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time           : 18-9-20 下午3:26
# @Author         : Tom.Lee
# @File           : middleware.py
# @Product        : PyCharm
# @Docs           : 
# @Source         : 

from django.utils.deprecation import MiddlewareMixin

from .common_funcs import ignore_self_waning
from .logger import ConsoleLogger

logger = ConsoleLogger()


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

