#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author         : Tom.Lee

import json
from datetime import datetime


class T(object):
    """
    object ==> vars(object) ==> dict str
    """

    def __str__(self):
        """程序显示结果时调用该函数"""
        return "<__main__.{} object {}>".format(
            self.__class__.__name__, vars(self) or hex(id(T)))

    def __repr__(self):
        """Python 对象互相调用时使用该函数"""
        return self.__str__()

    def to_dict(self):
        try:
            # 如果是django 模型，使用这种方式进行json转换
            from django.db import models
            if isinstance(self, models.Model):
                keys = list(map(lambda x: x.name, self._meta.fields))
                d = {}
                for k in keys:
                    v = getattr(self, k)
                    if isinstance(v, T):
                        v = v.to_dict()
                    if isinstance(v, datetime):
                        v = v.strftime("%Y-%m-%d %H:%M:%S")
                    d[k] = v
                return d
        except ImportError:
            # 如果是普通模型，使用这种方式进行json转换
            d = vars(self).copy()
            [d.pop(k) for k in list(filter(lambda x: x.startswith('_'), d.keys()))]
            for i in filter(lambda x: isinstance(d[x], T), d):
                d[i] = d[i].to_dict()
            return d

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)


def dict_filters(dic, pl):
    return {p: dic.get(p) for p in pl}


def ignore_self_waning(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
