#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author         : Tom.Lee
import os
import platform
import sys
import time
from typing import List, Dict, Any, Optional

import django
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms import forms
from django.urls import URLPattern, URLResolver
from django.urls.resolvers import RoutePattern, RegexPattern

from .file_tools import copy_file
from .file_tools import rename_file
from .http_funcs import json_response
from .route_decorator import route
from .route_decorator import route_class
from ..settings import UPLOAD_DIR


class UploadObjectForm(forms.Form):
    """
    docs: https://github.com/amlyj/horizon/blob/master/openstack_dashboard/api/rest/swift.py

    使用方法：
        form = UploadObjectForm(request.POST, request.FILES)
        if not form.is_valid():
            print '数据不能为空'
        data = form.clean()
        object_file = data['file']
        print 'file_name: %s' % object_file.name
        print 'file_size: %s' % object_file.size
    """
    file = forms.FileField(required=False)


@json_response
def save_file(request):
    form = UploadObjectForm(request.POST, request.FILES)
    if not form.is_valid():
        return {
            'status': False,
            'timestamp': int(round(time.time() * 1000)),
            'data': None,
            'path': request.path,
            'method': request.method,
            'message': '上传失败！ 文件不能为空.'
        }
    data = form.clean()
    object_file = data['file']
    # print('file_name: %s' % object_file.name)
    # print('file_size: %s' % object_file.size)
    save_path = '{upload_dir}/{name}'.format(upload_dir=UPLOAD_DIR, name=object_file.name)
    if isinstance(object_file, InMemoryUploadedFile):
        # 假如是内存类型的文件，即是小文件,直接写入文件
        with open(save_path, 'wb') as desc:
            for chunk in object_file.chunks():
                desc.write(chunk)
    else:
        # 假如是大文件，系统默认直接rename, 即更新linux文件的inode
        _func = rename_file
        # window环境使用copyfile, rename 会有权限问题
        if platform.system() == 'Windows':
            _func = copy_file
        _func(object_file.file.name, save_path)

    return {
        'status': True,
        'timestamp': int(round(time.time() * 1000)),
        'data': {
            'path': save_path,
            'size': object_file.size
        },
        'path': request.path,
        'method': request.method,
        'message': '文件 [%s] 上传成功！' % object_file.name
    }


def page_not_found(request, e):
    """
    404 page config
    :param request:
    :param e : exception
    :return:
    """
    from django.shortcuts import render
    if e:
        print("404 异常：", e)
    return render(request, 'error/404.html')


def make_path_view(urlconf, app_name, namespace=None):
    """
    构建 from django.urls import path 函数中的 view 变量
    .
    :param urlconf: re_path 列表 [re_path('index', student_index), re_path(r'([0-9a-zA-Z]*)', student_handler),]
    :param app_name: 应用名称
    :param namespace: 应用所在模块
    :return: tuple
    """
    return urlconf, app_name, namespace or app_name


class DjangoURLPrinter(object):
    """
    Django URL打印工具

    功能：
    1. 递归遍历Django项目中的所有URL配置
    2. 打印所有URL模式，包括带前缀的路径
    3. 处理include()引用的子路径
    4. 支持正则表达式和路径转换器
    5. 显示URL名称和视图函数信息

    使用方法：
    1. 在Django项目中导入此模块
    2. 调用 print_all_urls() 函数
    3. 或者调用 get_all_urls() 获取URL列表进行自定义处理
    """

    def __init__(self, show_view_names: bool = True, show_url_names: bool = True):
        """
        初始化URL打印器

        Args:
            show_view_names: 是否显示视图函数名称
            show_url_names: 是否显示URL名称
        """
        self.show_view_names = show_view_names
        self.show_url_names = show_url_names
        self.url_list = []

    @staticmethod
    def _get_pattern_string(pattern) -> str:
        """
        获取URL模式字符串

        Args:
            pattern: URL模式对象

        Returns:
            str: 格式化的模式字符串
        """
        if hasattr(pattern, 'pattern'):
            if isinstance(pattern.pattern, RoutePattern):
                return getattr(pattern.pattern, '_route')
            if isinstance(pattern.pattern, RegexPattern):
                return f"^{pattern.pattern.regex.pattern}$"
        return str(pattern)

    @staticmethod
    def _get_view_info(url_pattern) -> Dict[str, Any]:
        """
        获取视图信息，包括HTTP方法

        Args:
            url_pattern: URL模式对象

        Returns:
            Dict: 包含视图信息的字典
        """
        view_info = {
            'view_name': None,
            'view_class': None,
            'view_module': None,
            'http_methods': []
        }

        if hasattr(url_pattern, 'callback'):
            callback = url_pattern.callback
            if callback:
                view_info['view_name'] = getattr(callback, '__name__', str(callback))
                view_info['view_class'] = getattr(callback, '__qualname__', None)
                view_info['view_module'] = getattr(callback, '__module__', None)

                # 获取HTTP方法
                view_info['http_methods'] = DjangoURLPrinter._get_http_methods(callback)

        return view_info

    @staticmethod
    def _get_http_methods(view_func) -> List[str]:
        """
        获取视图支持的HTTP方法

        Args:
            view_func: 视图函数或类

        Returns:
            List[str]: HTTP方法列表
        """
        methods = set()

        try:
            # 检查函数视图的装饰器或属性
            if hasattr(view_func, 'allowed_methods'):
                methods.update(view_func.allowed_methods)

            # 检查require_http_methods装饰器
            if hasattr(view_func, 'view_class'):
                # 类视图
                view_class = view_func.view_class
                if hasattr(view_class, 'http_method_names'):
                    methods.update([m.upper() for m in view_class.http_method_names if m != 'options'])
                else:
                    # 检查类中定义的方法
                    for method in ['get', 'post', 'put', 'patch', 'delete', 'head']:
                        if hasattr(view_class, method):
                            methods.add(method.upper())

            elif hasattr(view_func, 'cls'):
                # ViewSet或其他基于类的视图
                view_class = view_func.cls
                if hasattr(view_class, 'http_method_names'):
                    methods.update([m.upper() for m in view_class.http_method_names if m != 'options'])

                # 检查ViewSet的actions
                if hasattr(view_func, 'actions'):
                    action_methods = view_func.actions.keys()
                    methods.update([m.upper() for m in action_methods])

            elif callable(view_func):
                # 函数视图
                # 检查装饰器添加的属性
                if hasattr(view_func, '__wrapped__'):
                    # 检查被装饰的函数
                    wrapped = view_func.__wrapped__
                    # 处理兼容一些第三方库，比如 django-decorator-plus
                    # 这些库可能会在被装饰的函数上设置 allowed_methods 属性来存储允许的HTTP方法列表
                    if hasattr(wrapped, 'allowed_methods'):
                        methods.update(wrapped.allowed_methods)
                    # 处理 @route 自定义的装饰器
                    if hasattr(wrapped, '_route_info'):
                        methods.update(getattr(wrapped, '_route_info', {}).get('methods', ['GET']))

                # 默认情况下，函数视图支持GET和POST
                if not methods:
                    methods.add('GET')
                    # 检查是否可能支持POST（通过函数名或参数推断）
                    func_name = getattr(view_func, '__name__', '').lower()
                    if any(keyword in func_name for keyword in ['create', 'post', 'submit', 'save', 'update']):
                        methods.add('POST')

            # 如果没有找到任何方法，默认为GET
            if not methods:
                methods.add('GET')

        except Exception as _err:
            _ = _err
            # 如果出现任何错误，默认返回GET
            methods.add('GET')

        return sorted(list(methods))

    def _extract_urls_recursive(self, urlpatterns, prefix: str = '') -> List[Dict[str, Any]]:
        """
        递归提取URL模式

        Args:
            urlpatterns: URL模式列表
            prefix: URL前缀

        Returns:
            List[Dict]: URL信息列表
        """
        urls = []

        for pattern in urlpatterns:
            if isinstance(pattern, URLResolver):
                # 处理include()的情况
                pattern_str = self._get_pattern_string(pattern)
                new_prefix = prefix + pattern_str.rstrip('$').lstrip('^')
                # 递归处理子URL
                try:
                    sub_urls = self._extract_urls_recursive(pattern.url_patterns, new_prefix)
                    urls.extend(sub_urls)
                except Exception as e:
                    urls.append({
                        'url': new_prefix,
                        'name': getattr(pattern, 'url_name', None),
                        'view_info': {'error': f"无法解析子URL: {e}"},
                        'type': 'resolver_error'
                    })

            elif isinstance(pattern, URLPattern):
                # 处理具体的URL模式
                pattern_str = self._get_pattern_string(pattern)
                full_url = prefix + pattern_str.rstrip('$').lstrip('^')
                view_info = self._get_view_info(pattern)
                urls.append({
                    'url': full_url,
                    'name': getattr(pattern, 'name', None),
                    'view_info': view_info,
                    'type': 'pattern'
                })

        return urls

    def get_all_urls(self, root_urlconf: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取所有URL配置

        Args:
            root_urlconf: 根URL配置模块，默认使用settings.ROOT_URLCONF

        Returns:
            List[Dict]: 所有URL信息列表
        """
        if not django:
            raise ImportError("Django未安装或未正确配置")

        # 确保Django已配置
        if not settings.configured:
            raise RuntimeError("Django settings未配置")

        # 获取根URL配置
        if root_urlconf is None:
            root_urlconf = settings.ROOT_URLCONF

        try:
            # 动态导入URL配置模块
            from django.urls import get_resolver
            resolver = get_resolver(root_urlconf)

            # 递归提取所有URL
            self.url_list = self._extract_urls_recursive(resolver.url_patterns)
            return self.url_list

        except Exception as e:
            raise RuntimeError(f"无法获取URL配置: {e}")

    def print_urls(self, urls: Optional[List[Dict[str, Any]]] = None,
                   sort_by_url: bool = True) -> None:
        """
        打印URL列表

        Args:
            urls: URL列表，默认使用get_all_urls()的结果
            sort_by_url: 是否按URL排序
        """
        if urls is None:
            urls = self.url_list if self.url_list else self.get_all_urls()

        if sort_by_url:
            urls = sorted(urls, key=lambda x: x['url'])

        print("\n" + "=" * 80)
        print("Django项目所有URL配置（包含HTTP方法）")
        print("=" * 80)
        print(f"总计发现 {len(urls)} 个URL模式\n")

        for i, url_info in enumerate(urls, 1):
            url = url_info['url']
            name = url_info.get('name')
            view_info = url_info.get('view_info', {})
            url_type = url_info.get('type', 'unknown')
            http_methods = view_info.get('http_methods', [])

            print(f"{i:3d}. URL: /{url.lstrip('/')}")

            # 显示HTTP方法
            if http_methods:
                methods_str = ', '.join(http_methods)
                print(f"     方法: [{methods_str}]")

            if self.show_url_names and name:
                print(f"     名称: {name}")

            if self.show_view_names and view_info:
                if 'error' in view_info:
                    print(f"     错误: {view_info['error']}")
                else:
                    view_name = view_info.get('view_name')
                    view_module = view_info.get('view_module')
                    if view_name:
                        print(f"     视图: {view_name}")
                    if view_module:
                        print(f"     模块: {view_module}")

            print(f"     类型: {url_type}")
            print()

    def export_to_file(self, filename: str, urls: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        导出URL列表到文件

        Args:
            filename: 输出文件名
            urls: URL列表，默认使用get_all_urls()的结果
        """
        if urls is None:
            urls = self.url_list if self.url_list else self.get_all_urls()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Django项目URL配置导出（包含HTTP方法）\n")
            f.write("=" * 50 + "\n")
            f.write(f"总计: {len(urls)} 个URL模式\n\n")

            for i, url_info in enumerate(urls, 1):
                url = url_info['url']
                name = url_info.get('name')
                view_info = url_info.get('view_info', {})
                http_methods = view_info.get('http_methods', [])

                f.write(f"{i}. /{url.lstrip('/')}\n")
                if http_methods:
                    methods_str = ', '.join(http_methods)
                    f.write(f"   方法: [{methods_str}]\n")
                if name:
                    f.write(f"   名称: {name}\n")
                if view_info and view_info.get('view_name'):
                    f.write(f"   视图: {view_info['view_name']}\n")
                f.write("\n")

        print(f"URL列表已导出到: {filename}")


def print_all_urls(show_view_names: bool = True,
                   show_url_names: bool = True,
                   sort_by_url: bool = True) -> None:
    """
    打印Django项目中的所有URL及其HTTP方法

    Args:
        show_view_names: 是否显示视图函数名称
        show_url_names: 是否显示URL名称
        sort_by_url: 是否按URL排序
    """
    printer = DjangoURLPrinter(show_view_names, show_url_names)
    urls = printer.get_all_urls()
    printer.print_urls(urls, sort_by_url)


def get_all_urls(root_urlconf: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    获取Django项目中的所有URL配置及其HTTP方法

    Args:
        root_urlconf: 根URL配置模块

    Returns:
        List[Dict]: URL信息列表
    """
    printer = DjangoURLPrinter()
    return printer.get_all_urls(root_urlconf)


def print_methods_summary() -> None:
    """
    打印HTTP方法使用统计摘要
    """
    printer = DjangoURLPrinter()
    urls = printer.get_all_urls()

    method_count = {}
    total_urls = len(urls)

    for url_info in urls:
        view_info = url_info.get('view_info', {})
        methods = view_info.get('http_methods', [])

        for method in methods:
            method_count[method] = method_count.get(method, 0) + 1

    print("\n" + "=" * 50)
    print("HTTP方法使用统计")
    print("=" * 50)
    print(f"总URL数量: {total_urls}")
    print("\n各HTTP方法使用情况:")

    for method, count in sorted(method_count.items()):
        percentage = (count / total_urls) * 100 if total_urls > 0 else 0
        print(f"  {method:8s}: {count:3d} 个URL ({percentage:5.1f}%)")

    print()


def export_urls_with_methods_to_csv(filename: str = 'django_urls_with_methods.csv') -> None:
    """
    导出URL列表及HTTP方法到CSV文件

    Args:
        filename: 输出文件名
    """
    import csv

    printer = DjangoURLPrinter()
    urls = printer.get_all_urls()

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['序号', 'URL', 'HTTP方法', 'URL名称', '视图函数', '视图模块', '类型']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for i, url_info in enumerate(urls, 1):
            view_info = url_info.get('view_info', {})
            methods = view_info.get('http_methods', [])

            writer.writerow({
                '序号': i,
                'URL': f"/{url_info['url'].lstrip('/')}",
                'HTTP方法': ', '.join(methods),
                'URL名称': url_info.get('name', ''),
                '视图函数': view_info.get('view_name', ''),
                '视图模块': view_info.get('view_module', ''),
                '类型': url_info.get('type', 'unknown')
            })

    print(f"URL列表已导出到CSV文件: {filename}")


def setup_django_environment(settings_module: str = None,
                             project_path: str = None) -> None:
    """
    设置Django环境

    Args:
        settings_module: Django设置模块路径
        project_path: Django项目路径
    """
    if project_path:
        sys.path.insert(0, project_path)

    if settings_module:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

    if django and not settings.configured:
        django.setup()


@route_class
class DjangoPath:
    """注册全局URL路径"""

    @route("/api/v1/paths")
    @json_response
    def urls(self, request):
        return get_all_urls()
