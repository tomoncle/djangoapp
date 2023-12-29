#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author         : Tom.Lee

import json
from datetime import datetime


class T(object):
    """
    使用示例：

    class A(T):
        def __init__(self, name, age):
            self.name = name
            self.age = age


    a1, a2 = A("jack", 29), A("tom", 30)
    print(a1, a2)
    # <__main__.A object {'name': 'jack', 'age': 29}> <__main__.A object {'name': 'tom', 'age': 30}>

    a1.sex = "male"
    a1.parent = a2
    print(a1.to_dict())
    # {'name': 'jack', 'age': 29, 'sex': 'male', 'parent': {'name': 'tom', 'age': 30}}
    """

    def __str__(self):
        """
        程序显示结果时调用该函数
        object ==> vars(object) ==> dict{}
        """
        return "<__main__.{} object {}>".format(self.__class__.__name__, vars(self) or hex(id(T)))

    def __repr__(self):
        """Python 对象互相调用时使用该函数"""
        return self.__str__()

    @staticmethod
    def getvalue(self, name):
        value = getattr(self, name)
        if isinstance(value, T):
            value = value.to_dict()
        if isinstance(value, datetime):
            value = value.strftime("%Y-%m-%d %H:%M:%S")
        return value

    def to_dict(self):
        try:
            from django.db import models
        except ImportError:
            models = None

        # 如果是django 模型，使用这种方式进行json转换
        if models and isinstance(self, models.Model):
            return {k: T.getvalue(self, k) for k in list(map(lambda x: x.name, self._meta.fields))}

        # 如果是普通模型，使用这种方式进行json转换
        dic = vars(self).copy()
        # 去掉 _开头 的隐藏属性
        [dic.pop(k) for k in list(filter(lambda x: x.startswith('_'), dic.keys()))]
        return {k: T.getvalue(self, k) for k in dic.keys()}

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)


def dict_filters(dic, keys):
    return {k: dic.get(k) for k in keys}


def ignore_self_waning(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
