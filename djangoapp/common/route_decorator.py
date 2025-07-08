#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: tomoncle
# @Time: 2023/7/7 下午5:13
# @Site: https://github.com/tomoncle/djangoapp
# @File: routers.py
# @Software: PyCharm

"""
Django类装饰器 - 自动路由注册

使用方法:
1. 在类上使用 @route_class 装饰器
2. 在类方法上使用 @route 装饰器配置路由
3. 调用 register_routes() 自动注册所有路由

示例:
    # 不使用前缀
    @route_class
    class UserController:
        @route('/users/', methods=['GET'])
        def list_users(self, request):
            return JsonResponse({'users': []})

        @route('/users/<int:user_id>/', methods=['GET'])
        def get_user(self, request, user_id):
            return JsonResponse({'user_id': user_id})

    # 使用前缀
    @route_class(prefix='/api/v1')
    class ApiController:
        @route('/users/', methods=['GET'])  # 实际路由: /api/v1/users/
        def list_users(self, request):
            return JsonResponse({'users': []})

        @route('/products/', methods=['GET'])  # 实际路由: /api/v1/products/
        def list_products(self, request):
            return JsonResponse({'products': []})
"""

import inspect
import re
from functools import wraps
from typing import Any, Type

from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from loguru import logger

try:
    from .route_discover import ensure_routes_discovered, force_rediscover_routes
except ImportError:
    # 如果无法导入，提供空实现
    def ensure_routes_discovered():
        return {'total_count': 0, 'message': '自动发现功能未启用'}


    def force_rediscover_routes():
        return {'total_count': 0, 'message': '自动发现功能未启用'}

# 全局路由注册表
_registered_routes = []
_registered_classes = []

__all__ = [
    'route',
    'route_class',
    'register_routes',
    'get_registered_routes',
]


def route(url_pattern, methods=None, name=None, csrf_exempt_flag=True):
    """
    方法装饰器 - 配置路由信息

    Args:
        url_pattern (str): URL模式，支持Django URL模式
        methods (list): 允许的HTTP方法，默认为['GET']
        name (str): 路由名称，默认为None
        csrf_exempt_flag (bool): 是否免除CSRF验证，默认为True

    Returns:
        function: 装饰后的方法
    """
    if methods is None:
        methods = ['GET']

    def decorator(func):
        # 在函数上添加路由信息
        func._route_info = {
            'url_pattern': url_pattern,
            'methods': methods,
            'name': name or f"{func.__name__}",
            'csrf_exempt': csrf_exempt_flag
        }
        return func

    return decorator


def route_class(prefix=''):
    """
    类装饰器 - 标记类为路由控制器

    Args:
        prefix (str): URL前缀，默认为空字符串

    Returns:
        function: 装饰器函数

    注意：当django app 引用 route_class 和 route 装饰器时，并没有其他模块引用改 app 的 views.py 模块，则无法被扫描，
    1. 在 settings.py 中注册 app
    2. 在当前 app 的 __init__.py 中引用对应的类对象 from .views import DemoController, ApiController 就可以了
    """

    def decorator(cls: Type[Any]) -> Type[Any]:
        """
        实际执行过程是：
        1. Python 首先创建 被装饰的 类对象，例如 UserController
        2. 将这个类对象作为参数传递给 decorator 函数
        3. 在 decorator 函数中， cls 就是 UserController 这个类对象
        4. 函数给类添加属性： cls._is_route_controller = True
        5. 返回修改后的类对象
        :param cls: 所以 cls 就是被装饰的类本身，装饰器通过修改这个类对象来添加路由相关的元数据
        :return:修改后的类对象
        """
        # 标记类为路由控制器
        cls._is_route_controller = True
        cls._url_prefix = prefix

        # 收集类中所有带有路由信息的方法
        route_methods = []
        for method_name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, '_route_info'):
                route_methods.append((method_name, method))

        # 将路由信息存储到类上
        cls._route_methods = route_methods

        # 注册到全局列表
        _registered_classes.append(cls)

        return cls

    # 支持两种使用方式：@route_class 和 @route_class(prefix='/api')
    # 无前缀：@route_class
    # 等价于：route_class(ExampleController)
    # prefix = ExampleController (类对象)

    # 有前缀：@route_class(prefix='/api')
    # 等价于：route_class('/api')(ApiController)
    # 第一步：route_class('/api') 返回 decorator 函数
    # 第二步：decorator(ApiController) 处理类对象

    # 不加括号 和 加空括号 是完全不同的：
    #
    # - @ route_class → 直接传递类对象
    # - @ route_class() → 使用默认参数，然后传递类对象
    if isinstance(prefix, type):
        # 直接使用 @route_class 没有前缀的情况
        _cls = prefix
        prefix = ''
        return decorator(_cls)
    else:
        # 使用 @route_class(prefix='/api') 的情况
        return decorator


def create_view_function(cls, method_name, method, route_info):
    """
    创建Django视图函数

    Args:
        cls: 控制器类
        method_name (str): 方法名
        method: 方法对象
        route_info (dict): 路由信息

    Returns:
        function: Django视图函数
    """

    @wraps(method)
    def view_function(request, *args, **kwargs):
        # 创建类实例
        instance = cls()

        # 调用方法
        return method(instance, request, *args, **kwargs)

    # 应用HTTP方法限制
    if route_info['methods']:
        view_function = require_http_methods(route_info['methods'])(view_function)

    # 应用CSRF豁免
    if route_info['csrf_exempt']:
        view_function = csrf_exempt(view_function)

    # 设置函数名称
    view_function.__name__ = f"{cls.__name__}_{method_name}"

    return view_function


def convert_url_pattern(pattern):
    """
    转换URL模式，支持简化的参数语法

    Args:
        pattern (str): 原始URL模式

    Returns:
        str: 转换后的Django URL模式
    """
    # 转换 <int:id> 格式为 Django 格式
    pattern = re.sub(r'<int:(\w+)>', r'(?P<\1>\\d+)', pattern)
    pattern = re.sub(r'<str:(\w+)>', r'(?P<\1>[^/]+)', pattern)
    pattern = re.sub(r'<slug:(\w+)>', r'(?P<\1>[-a-zA-Z0-9_]+)', pattern)
    pattern = re.sub(r'<uuid:(\w+)>', r'(?P<\1>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', pattern)

    return pattern


def register_routes(auto_discover=True):
    """
    注册所有路由到Django URL配置

    Args:
        auto_discover (bool): 是否在注册前自动发现路由，默认为True

    Returns:
        list: Django URL模式列表
    """
    # 自动发现路由（如果启用）
    if auto_discover:
        try:
            discovery_results = ensure_routes_discovered()
            if discovery_results.get('total_count', 0) > 0:
                logger.info(f"自动发现完成，总共引入了 {discovery_results['total_count']} 个路由控制器")
        except Exception as e:
            logger.warning(f"自动发现路由时出错: {e}")

    urlpatterns = []

    for cls in _registered_classes:
        if not hasattr(cls, '_route_methods'):
            continue

        # 获取类的URL前缀
        prefix = getattr(cls, '_url_prefix', '')

        for method_name, method in cls._route_methods:
            # route_info = method._route_info
            route_info = getattr(method, '_route_info')

            # 创建视图函数
            view_func = create_view_function(cls, method_name, method, route_info)

            # 应用前缀到URL模式
            original_pattern = route_info['url_pattern']
            if prefix:
                # 确保前缀以/开头，不以/结尾
                prefix = prefix.strip('/')
                if prefix:
                    prefix = '/' + prefix
                # 确保原始模式以/开头
                if not original_pattern.startswith('/'):
                    original_pattern = '/' + original_pattern
                # 组合前缀和原始模式
                full_pattern = prefix + original_pattern
            else:
                full_pattern = original_pattern

            # 转换URL模式
            url_pattern = convert_url_pattern(full_pattern)

            # 创建URL模式
            if '<' in url_pattern or '(' in url_pattern:
                # 使用正则表达式模式
                url_entry = re_path(url_pattern.lstrip('/'), view_func, name=route_info['name'])
            else:
                # 使用简单路径模式
                url_entry = path(url_pattern.lstrip('/'), view_func, name=route_info['name'])

            urlpatterns.append(url_entry)

            # 记录注册信息（包含完整的URL模式）
            _registered_routes.append({
                'class': cls.__name__,
                'method': method_name,
                'url_pattern': full_pattern,
                'original_pattern': route_info['url_pattern'],
                'prefix': prefix,
                'methods': route_info['methods'],
                'name': route_info['name']
            })

    return urlpatterns


def get_registered_routes():
    """
    获取已注册的路由信息

    Returns:
        list: 路由信息列表
    """
    return _registered_routes.copy()


def print_routes():
    """
    打印所有已注册的路由信息
    """
    logger.info("=== 已注册的路由 ===")
    for r in _registered_routes:
        methods_str = ', '.join(r['methods'])
        logger.info(f"{r['class']}.{r['method']}: {r['url_pattern']} [{methods_str}] (name: {r['name']})")
    logger.info(f"总计: {len(_registered_routes)} 个路由")


def clear_registered_routes():
    """
    清空已注册的路由（用于测试或重新加载）
    """
    global _registered_routes, _registered_classes
    _registered_routes.clear()
    _registered_classes.clear()
    logger.info("已清空所有注册的路由")


def rediscover_and_register():
    """
    强制重新发现并注册所有路由

    Returns:
        tuple: (urlpatterns, discovery_results)
    """
    # 清空现有注册
    clear_registered_routes()

    # 强制重新发现
    try:
        discovery_results = force_rediscover_routes()
        logger.info(f"重新发现了 {discovery_results.get('total_count', 0)} 个路由控制器")
    except Exception as e:
        logger.error(f"重新发现路由时出错: {e}")
        discovery_results = {'total_count': 0, 'errors': [str(e)]}

    # 注册路由（不再自动发现，因为已经强制发现过了）
    urlpatterns = register_routes(auto_discover=False)

    return urlpatterns, discovery_results


def get_route_statistics():
    """
    获取路由统计信息

    Returns:
        dict: 路由统计信息
    """
    stats = {
        'total_routes': len(_registered_routes),
        'total_classes': len(_registered_classes),
        'routes_by_class': {},
        'routes_by_method': {},
        'routes_with_prefix': 0,
        'routes_without_prefix': 0
    }

    for route in _registered_routes:
        # 按类统计
        class_name = route['class']
        if class_name not in stats['routes_by_class']:
            stats['routes_by_class'][class_name] = 0
        stats['routes_by_class'][class_name] += 1

        # 按HTTP方法统计
        for method in route['methods']:
            if method not in stats['routes_by_method']:
                stats['routes_by_method'][method] = 0
            stats['routes_by_method'][method] += 1

        # 按前缀统计
        if route['prefix']:
            stats['routes_with_prefix'] += 1
        else:
            stats['routes_without_prefix'] += 1

    return stats

# # 示例控制器类（不使用前缀）
# @route_class
# class ExampleController:
#     """
#     示例控制器类
#     """
#
#     @route('/api/hello/', methods=['GET'])
#     def hello(self, request):
#         """
#         简单的Hello接口
#         """
#         return JsonResponse({
#             'message': 'Hello, World!',
#             'method': request.method
#         })
#
#     @route('/api/users/', methods=['GET', 'POST'])
#     def users(self, request):
#         """
#         用户列表接口
#         """
#         if request.method == 'GET':
#             return JsonResponse({
#                 'users': [
#                     {'id': 1, 'name': '张三'},
#                     {'id': 2, 'name': '李四'}
#                 ]
#             })
#         elif request.method == 'POST':
#             return JsonResponse({
#                 'message': '用户创建成功',
#                 'method': request.method
#             })
#
#     @route('/api/users/<int:user_id>/', methods=['GET', 'PUT', 'DELETE'])
#     def user_detail(self, request, user_id):
#         """
#         用户详情接口
#         """
#         return JsonResponse({
#             'user_id': user_id,
#             'method': request.method,
#             'message': f'操作用户 {user_id}'
#         })
#
#     @route('/api/search/<str:keyword>/', methods=['GET'])
#     def search(self, request, keyword):
#         """
#         搜索接口
#         """
#         return JsonResponse({
#             'keyword': keyword,
#             'results': [f'结果1 for {keyword}', f'结果2 for {keyword}']
#         })
#
#
# # 使用前缀的控制器类
# @route_class(prefix='/api/v1')
# class ProductController:
#     """
#     产品控制器类
#     """
#
#     @route('/products/', methods=['GET'])  # 实际路由: /api/v1/products/
#     def list_products(self, request):
#         """
#         产品列表
#         """
#         return JsonResponse({
#             'products': [
#                 {'id': 1, 'name': '产品A', 'price': 100},
#                 {'id': 2, 'name': '产品B', 'price': 200}
#             ]
#         })
#
#     @route('/products/<int:product_id>/reviews/',
#            methods=['GET', 'POST'])  # 实际路由: /api/v1/products/<int:product_id>/reviews/
#     def product_reviews(self, request, product_id):
#         """
#         产品评论
#         """
#         return JsonResponse({
#             'product_id': product_id,
#             'method': request.method,
#             'reviews': ['评论1', '评论2']
#         })
#
#
# # 另一个使用不同前缀的控制器
# @route_class(prefix='/admin')
# class AdminController:
#     """
#     管理员控制器类
#     """
#
#     @route('/dashboard/', methods=['GET'])  # 实际路由: /admin/dashboard/
#     def dashboard(self, request):
#         """
#         管理员仪表板
#         """
#         return JsonResponse({
#             'message': '管理员仪表板',
#             'user_count': 100,
#             'product_count': 50
#         })
#
#     @route('/users/manage/', methods=['GET', 'POST'])  # 实际路由: /admin/users/manage/
#     def manage_users(self, request):
#         """
#         用户管理
#         """
#         return JsonResponse({
#             'message': '用户管理页面',
#             'method': request.method
#         })

# if __name__ == '__main__':
#     # 测试代码
#     print("Django路由装饰器测试")
#
#     # 注册路由
#     urlpatterns = register_routes()
#
#     # 打印路由信息
#     print_routes()
#
#     # 打印URL模式
#     print("=== URL模式 ===")
#     for pattern in urlpatterns:
#         print(f"{pattern.pattern} -> {pattern.callback.__name__}")
