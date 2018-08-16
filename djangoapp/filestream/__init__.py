#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author         : Tom.Lee
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import StreamingHttpResponse

from ..common import get_file_bytes
from ..common import open_file_to_iterable


def download(request):
    """
    Html
       <a href="/web/download">下载</a>

    适合下载比较小的文件
    :param request:
    :return:HttpResponse
    """
    file_path = request.GET.get('file_path')
    if not file_path:
        return HttpResponseBadRequest(HttpResponse("400 Bad Request."))
    response = HttpResponse()
    response['Content-Type'] = 'application/binary; charset=utf-8'
    response['Content-Disposition'] = ('attachment; filename=%s' % file_path)
    # 小文件不要写"response['Content-Length']",否则会丢失数据或不能下载
    with open(file_path) as f:
        for line in f:
            # 写入内容
            print(line)
            response.write(line)
    return response


def download_large(request):
    """
    <a href="/web/download_large">下载</a>

    下载比较庞大的文件，使用StreamingHttpResponse对象

    content_length = int(resp.headers.get('content-length', 0))

    :param request:
    :return: StreamingHttpResponse 流对象
    """
    file_path = request.GET.get('file_path')
    if not file_path:
        return HttpResponseBadRequest(HttpResponse("400 Bad Request."))
    try:
        data = open_file_to_iterable(file_path)
        response = StreamingHttpResponse(data)  # data必须是可迭代对象
        response['Content-Type'] = 'application/binary; charset=utf-8'
        response['Content-Disposition'] = ('attachment; filename=%s' % file_path)
        response['Content-Length'] = get_file_bytes(file_path)
        return response
    except Exception as e:
        return HttpResponse('下载失败！ "{}"'.format(e))


def upload(request):
    pass


def _urls():
    """
    files handler urlpatterns
    :return:
    """
    from django.conf.urls import url
    urlpatterns = [
        url(r'^download/$', download),
        url(r'^dl_large/$', download_large),
        url(r'^upload/$', upload),
    ]

    return urlpatterns, 'file_stream', 'file_stream'


# urlpatterns
urls = _urls()
