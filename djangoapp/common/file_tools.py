#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author         : Tom.Lee


import errno
import os
from functools import reduce

import six

__all__ = ['IterableWithLength',
           'open_file_to_iterable',
           'get_file_bytes',
           'file_iterator',
           'get_file_size']


class IterableWithLength(object):
    """
    返回可迭代对象及对象大小
    """

    def __init__(self, iterable, length):
        self.iterable = iterable
        self.length = length

    def __iter__(self):
        try:
            for chunk in self.iterable:
                yield chunk
        finally:
            self.iterable.close()

    def next(self):
        return next(self.iterable)

    def __len__(self):
        return self.length


def open_file_to_iterable(file_path):
    """
    打开文件并返回可迭代对象
    :param file_path:
    :return: 可迭代对象
    """
    with open(file_path, 'rb') as f:  # mode=rb 表示以二进制模式打开,避免乱码
        for line in f:
            yield line


def get_file_bytes(file_path):
    """
    获取对象长度
    速度比较慢, 推荐使用 get_file_size()
    :param file_path:
    :return:
    """

    def prod(x, y):
        return x + y

    return reduce(prod, [len(b) for b in open_file_to_iterable(file_path)])


def file_iterator(file_name, chunk_size=512):
    """
    按一定大小读取文件
    :param file_name:
    :param chunk_size:
    :return: 可迭代对象
    """
    with open(file_name, 'rb') as f:  # mode=rb 表示以二进制模式打开,避免乱码
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


def get_file_size(file_obj):
    """获取文件对象的大小
        get_file_size(open('/home/ubuntu-14.04.3-desktop-amd64.iso'))

    :param file_obj: file-like object.
    """
    if (hasattr(file_obj, 'seek') and hasattr(file_obj, 'tell') and
            (six.PY2 or six.PY3 and file_obj.seekable())):
        try:
            curr = file_obj.tell()
            file_obj.seek(0, os.SEEK_END)
            size = file_obj.tell()
            file_obj.seek(curr)
            return size
        except IOError as e:
            if e.errno == errno.ESPIPE:
                # Illegal seek. This means the file object
                # is a pipe (e.g. the user is trying
                # to pipe image data to the client,
                # echo testdata | bin/glance add blah...), or
                # that file object is empty, or that a file-like
                # object which doesn't support 'seek/tell' has
                # been supplied.
                return
            else:
                raise
