#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author         : Tom.Lee
import requests
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import StreamingHttpResponse

from ..common import get_file_size
from ..common import open_file_to_iterable
from ..common import save_file
from ..settings import UPLOAD_DIR

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

    file_name = file_path.split("/")[-1:][0].split("?")[0]
    try:
        data = open_file_to_iterable(file_path)
        response = StreamingHttpResponse(data)  # data必须是可迭代对象
        response['Content-Type'] = 'application/binary; charset=utf-8'
        response['Content-Disposition'] = ('attachment; filename=%s' % file_name)
        response['Content-Length'] = get_file_size(open(file_path))
        return response
    except Exception as e:
        return HttpResponse('下载失败！ "{}"'.format(e))


def download_proxy(request):
    headers = {
        'Cookie': '',
        'accept-encoding': 'gzip, deflate, br',
        'accept': 'text/html,application/xhtml+xml,application/xml;'
                  'q=0.9,image/webp,image/apng,*/*;q=0.8',
        'cache-control': 'max-age=0',
        'Connection': 'keep-alive',
        'upgrade-insecure-requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; '
                      'SM-G900P Build/LRX21T) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 '
                      'Mobile Safari/537.36',
    }
    url = request.GET.get('url')
    if not url:
        return HttpResponseBadRequest(HttpResponse("400 Bad Request."))

    file_name = url.split("/")[-1:][0].split("?")[0]
    try:
        res = requests.get(url, headers=headers, stream=True, verify=False)

        def g():
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk

        response = StreamingHttpResponse(g())  # data必须是可迭代对象
        response['Content-Type'] = 'application/binary; charset=utf-8'
        response['Content-Disposition'] = ('attachment; filename=%s' % file_name)
        response['Content-Length'] = float(res.headers.get('Content-Length', default=0))
        return response
    except Exception as e:
        return HttpResponse('下载失败！ "{}"'.format(e))


def upload(request):
    if request.method == 'GET':
        return HttpResponse("""
         <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
        """)
    return save_file(request)


def _urls():
    """
    files handler urlpatterns
    :return:
    """
    from django.conf.urls import url
    urlpatterns = [
        url(r'^download/$', download),
        url(r'^dl_large/$', download_large),
        url(r'^dl_proxy/$', download_proxy),
        url(r'^upload/$', upload),
    ]

    return urlpatterns, 'file_stream', 'file_stream'


# urlpatterns
urls = _urls()
