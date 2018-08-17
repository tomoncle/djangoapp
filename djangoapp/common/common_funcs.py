#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author         : Tom.Lee

import json


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
