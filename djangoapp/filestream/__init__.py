#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/6 22:41
# @Author  : tomoncle
# @Site    : https://github.com/tomoncle
# @File    : __init__.py.py
import io
import json
from datetime import datetime

import requests
import xlrd
import xlwt
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseBadRequest
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..common import get_file_size
from ..common import open_file_to_iterable
from ..common import save_file

# 示例数据
SAMPLE_DATA = [
    {
        "节点名称": "node93",
        "IP": "10.1.7.93",
        "操作系统": "linux",
        "用户名称": "root",
        "密码": "123456",
        "所属组": "测试",
        "端口": "22"
    },
    {
        "节点名称": "node94",
        "IP": "10.1.7.94",
        "操作系统": "windows",
        "用户名称": "administrator",
        "密码": "Admin123!",
        "所属组": "生产",
        "端口": "3389"
    },
    {
        "节点名称": "node95",
        "IP": "10.1.7.95",
        "操作系统": "linux",
        "用户名称": "ubuntu",
        "密码": "Ubuntu@2024",
        "所属组": "开发",
        "端口": "22"
    }
]


def create_excel_file(data=None):
    """
    创建Excel文件

    Args:
        data: 数据列表，如果为None则使用示例数据

    Returns:
        BytesIO: Excel文件的字节流
    """
    if data is None:
        data = SAMPLE_DATA

    # 创建工作簿和工作表
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    # 定义表头
    headers = ["节点名称", "IP", "操作系统", "用户名称", "密码", "所属组", "端口"]

    # 设置表头样式
    header_style = xlwt.XFStyle()

    # 字体样式：白色加粗
    header_font = xlwt.Font()
    header_font.bold = True
    header_font.colour_index = xlwt.Style.colour_map['white']
    header_style.font = header_font

    # 背景颜色：蓝色
    header_pattern = xlwt.Pattern()
    header_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    header_pattern.pattern_fore_colour = xlwt.Style.colour_map['blue']
    header_style.pattern = header_pattern

    # 对齐方式：居中
    header_alignment = xlwt.Alignment()
    header_alignment.horz = xlwt.Alignment.HORZ_CENTER
    header_alignment.vert = xlwt.Alignment.VERT_CENTER
    header_style.alignment = header_alignment

    # 数据样式：居中对齐
    data_style = xlwt.XFStyle()
    data_alignment = xlwt.Alignment()
    data_alignment.horz = xlwt.Alignment.HORZ_CENTER
    data_alignment.vert = xlwt.Alignment.VERT_CENTER
    data_style.alignment = data_alignment

    # 写入表头
    for col_num, header in enumerate(headers):
        ws.write(0, col_num, header, header_style)
        # 设置列宽
        ws.col(col_num).width = 4000  # 约20个字符宽度

    # 写入数据
    for row_num, item in enumerate(data, 1):
        for col_num, header in enumerate(headers):
            value = item.get(header, "")
            ws.write(row_num, col_num, value, data_style)

    # 保存到内存
    excel_buffer = io.BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)

    return excel_buffer


@require_http_methods(["GET"])
def download_excel(request):
    """
    下载Excel文件接口

    Args:
        request: Django请求对象

    Returns:
        HttpResponse: Excel文件下载响应
    """
    try:
        # 创建Excel文件
        excel_buffer = create_excel_file()

        # 生成文件名（包含时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"节点信息_{timestamp}.xls"

        # 创建HTTP响应
        response = HttpResponse(
            excel_buffer.getvalue(),
            content_type='application/vnd.ms-excel'
        )

        # 设置文件下载头
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(excel_buffer.getvalue())

        return response

    except Exception as e:
        return HttpResponse(f'生成Excel文件失败！ "{e}"', status=500)


@require_http_methods(["POST"])
@csrf_exempt
def download_excel_custom(request):
    """
    自定义数据下载Excel文件接口

    Args:
        request: Django请求对象

    Request Body:
    {
        "data": [
            {
                "节点名称": "node1",
                "IP": "192.168.1.1",
                "操作系统": "linux",
                "用户名称": "root",
                "密码": "password",
                "所属组": "测试",
                "端口": "22"
            }
        ]
    }

    Returns:
        HttpResponse: Excel文件下载响应
    """
    try:
        # 解析请求数据
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "error": "请求数据格式错误",
                "message": "请提供有效的JSON数据"
            }, status=400)

        if 'data' not in request_data:
            return JsonResponse({
                "error": "请求数据格式错误",
                "message": "请提供data字段包含节点信息列表"
            }, status=400)

        data = request_data['data']
        if not isinstance(data, list) or len(data) == 0:
            return JsonResponse({
                "error": "数据格式错误",
                "message": "data字段必须是非空列表"
            }, status=400)

        # 创建Excel文件
        excel_buffer = create_excel_file(data)

        # 生成文件名（包含时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"自定义节点信息_{timestamp}.xls"

        # 创建HTTP响应
        response = HttpResponse(
            excel_buffer.getvalue(),
            content_type='application/vnd.ms-excel'
        )

        # 设置文件下载头
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(excel_buffer.getvalue())

        return response

    except Exception as e:
        return JsonResponse({
            "error": "生成Excel文件失败",
            "message": str(e)
        }, status=500)


@require_http_methods(["GET", "POST"])
@csrf_exempt
def upload_excel(request):
    """
    上传Excel文件并解析内容

    Args:
        request: Django请求对象

    Returns:
        JsonResponse: 解析结果
    """
    if request.method == 'GET':
        print("调用上传方法")
        return HttpResponse("""
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
            <input type=file name=file>
            <input type=submit value=Upload>
        </form>
        """)
    try:
        # 检查是否有文件上传
        if 'file' not in request.FILES:
            return JsonResponse({
                "error": "文件上传错误",
                "message": "请选择要上传的Excel文件"
            }, status=400)

        uploaded_file = request.FILES['file']

        # 检查文件类型
        if not uploaded_file.name.endswith(('.xls', '.xlsx')):
            return JsonResponse({
                "error": "文件格式错误",
                "message": "请上传.xls或.xlsx格式的Excel文件"
            }, status=400)

        # 读取Excel文件内容
        try:
            # 读取文件内容到内存
            file_content = uploaded_file.read()

            # 使用xlrd读取.xls文件
            if uploaded_file.name.endswith('.xls'):
                workbook = xlrd.open_workbook(file_contents=file_content)
            else:
                # 对于.xlsx文件，需要使用openpyxl或其他库
                return JsonResponse({
                    "error": "文件格式暂不支持",
                    "message": "当前仅支持.xls格式文件，请转换后重试"
                }, status=400)

            # 获取第一个工作表
            worksheet = workbook.sheet_by_index(0)

            # 解析数据
            parsed_data = []
            headers = ["节点名称", "IP", "操作系统", "用户名称", "密码", "所属组", "端口"]

            # 检查表头是否匹配（第一行）
            if worksheet.nrows > 0:
                # first_row = [worksheet.cell_value(0, col) for col in range(min(len(headers), worksheet.ncols))]
                # print(f"Excel文件表头: {first_row}")

                # 读取数据行（从第二行开始）
                for row_idx in range(1, worksheet.nrows):
                    row_data = {}
                    for col_idx, header in enumerate(headers):
                        if col_idx < worksheet.ncols:
                            cell_value = worksheet.cell_value(row_idx, col_idx)
                            # 处理不同类型的单元格值
                            if isinstance(cell_value, float) and cell_value.is_integer():
                                cell_value = str(int(cell_value))
                            else:
                                cell_value = str(cell_value).strip()
                            row_data[header] = cell_value
                        else:
                            row_data[header] = ""

                    # 只添加非空行
                    if any(row_data.values()):
                        parsed_data.append(row_data)
                        # print(f"解析数据行 {row_idx}: {row_data}")

            # print("\n=== Excel文件解析完成 ===")
            # print(f"文件名: {uploaded_file.name}")
            # print(f"文件大小: {uploaded_file.size} bytes")
            # print(f"工作表行数: {worksheet.nrows}")
            # print(f"工作表列数: {worksheet.ncols}")
            # print(f"解析到的数据条数: {len(parsed_data)}")
            # print(f"解析内容: {json.dumps(parsed_data, ensure_ascii=False, indent=2)}")

            return JsonResponse({
                "success": True,
                "message": "Excel文件解析成功",
                "file_info": {
                    "filename": uploaded_file.name,
                    "size": uploaded_file.size,
                    "rows": worksheet.nrows,
                    "cols": worksheet.ncols
                },
                "data": parsed_data,
                "count": len(parsed_data)
            }, json_dumps_params=dict(ensure_ascii=False))

        except xlrd.XLRDError as e:
            return JsonResponse({
                "error": "Excel文件读取失败",
                "message": f"文件格式错误或文件损坏: {str(e)}"
            }, status=400)

    except Exception as e:
        print(f"上传文件解析错误: {str(e)}")
        return JsonResponse({
            "error": "文件处理失败",
            "message": str(e)
        }, status=500)


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
        # data必须是可迭代对象
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

# def _urls():
#     """
#     files handler urlpatterns
#     :return:
#     """
#     from django.urls import re_path as url
#     urlpatterns = [
#         url(r'^download/$', download),
#         url(r'^dl_large/$', download_large),
#         url(r'^dl_proxy/$', download_proxy),
#         url(r'^upload/$', upload),
#     ]
#
#     return urlpatterns, 'file_stream', 'file_stream'
#
#
# # urlpatterns
# urls = _urls()
