#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: tomoncle
# @Time: 2025/7/7 下午7:14
# @Site: https://github.com/tomoncle/djangoapp
# @File: discover_routes.py
# @Software: PyCharm

"""
Django路由装饰器自动发现增强

解决问题：当新建Django app使用了路由装饰器但没有被其他地方引用时，
装饰器不会被扫描到的问题。

解决方案：
1. 自动扫描Django应用中的模块
2. 动态导入包含路由装饰器的模块
3. 提供配置选项控制扫描行为
"""

import importlib
import os

from django.apps import apps
from django.conf import settings
from loguru import logger


def autodiscover_routes(app_names=None, module_names=None, exclude_apps=None):
    """
    自动发现Django应用中的路由装饰器

    Args:
        app_names (list): 要扫描的应用名称列表，None表示扫描所有应用
        module_names (list): 要扫描的模块名称列表，默认为['views', 'controllers', 'apis']
        exclude_apps (list): 要排除的应用名称列表

    Returns:
        int: 发现的路由控制器类数量
    """
    if module_names is None:
        module_names = ['views', 'controllers', 'apis', 'routes']

    if exclude_apps is None:
        exclude_apps = []

    discovered_count = 0

    # 获取要扫描的应用列表
    if app_names is None:
        # 扫描所有已安装的应用
        target_apps = [app_config.name for app_config in apps.get_app_configs()]
    else:
        target_apps = app_names

    # 排除指定的应用
    target_apps = [app for app in target_apps if app not in exclude_apps]

    logger.debug(f"开始自动发现路由，扫描应用: {target_apps}")

    for app_name in target_apps:
        try:
            # 提取应用标签（去掉包路径前缀）
            app_label = app_name.split('.')[-1] if '.' in app_name else app_name

            # 获取应用配置
            try:
                app_config = apps.get_app_config(app_label)
            except LookupError:
                # 如果应用标签不存在，尝试使用完整名称
                try:
                    app_config = apps.get_app_config(app_name)
                except LookupError:
                    logger.warning(f"无法找到应用配置: {app_name} (标签: {app_label})")
                    continue

            app_module = app_config.module

            if app_module is None:
                continue

            # 使用应用模块的实际名称进行导入
            actual_app_name = app_config.name

            # 扫描应用中的指定模块
            for module_name in module_names:
                try:
                    # 尝试导入模块
                    full_module_name = f"{actual_app_name}.{module_name}"

                    # 检查是否已扫描过此模块
                    if _is_module_scanned(full_module_name):
                        cached_count = _get_cached_controller_count(full_module_name)
                        # discovered_count += cached_count
                        logger.debug(f"使用缓存结果: {full_module_name} ({cached_count} 个控制器)")
                        continue

                    module = importlib.import_module(full_module_name)

                    # 检查模块中是否有路由控制器
                    controller_count = _scan_module_for_controllers(module, full_module_name)

                    # 缓存扫描结果
                    _mark_module_scanned(full_module_name, controller_count)
                    discovered_count += controller_count

                    if controller_count > 0:
                        logger.debug(f"在 {full_module_name} 中发现 {controller_count} 个路由控制器")

                except ImportError:
                    # 模块不存在，跳过
                    continue
                except Exception as e:
                    logger.warning(f"扫描模块 {actual_app_name}.{module_name} 时出错: {e}")

        except Exception as e:
            logger.warning(f"扫描应用 {app_name} 时出错: {e}")

    logger.info(f"应用模式自动发现完成，总共发现 {discovered_count} 个路由控制器")
    return discovered_count


def autodiscover_with_pattern_cached(pattern='**/views.py', exclude_patterns=None):
    """
    使用文件模式自动发现路由（带缓存支持）

    Args:
        pattern (str): 文件匹配模式
        exclude_patterns (list): 要排除的模式列表

    Returns:
        tuple: (发现的路由控制器类数量, 跳过的模块数量)
    """
    import glob
    import fnmatch

    if exclude_patterns is None:
        exclude_patterns = ['**/migrations/**', '**/tests/**', '**/test_*.py']

    discovered_count = 0
    skipped_count = 0

    # 获取Django项目根目录
    base_dir = getattr(settings, 'BASE_DIR', os.getcwd())

    # 查找匹配的文件
    pattern_path = os.path.join(base_dir, pattern)
    matching_files = glob.glob(pattern_path, recursive=True)

    for file_path in matching_files:
        # 检查是否应该排除
        should_exclude = False
        for exclude_pattern in exclude_patterns:
            exclude_path = os.path.join(base_dir, exclude_pattern)
            if fnmatch.fnmatch(file_path, exclude_path):
                should_exclude = True
                break

        if should_exclude:
            continue

        try:
            # 将文件路径转换为模块名
            rel_path = os.path.relpath(file_path, base_dir)
            module_name = rel_path.replace(os.path.sep, '.').replace('.py', '')

            # 检查是否已扫描过此模块
            if _is_module_scanned(module_name):
                cached_count = _get_cached_controller_count(module_name)
                # discovered_count += cached_count
                skipped_count += 1
                logger.debug(f"跳过已扫描模块: {module_name} ({cached_count} 个控制器)")
                continue

            # 导入模块
            module = importlib.import_module(module_name)

            # 扫描控制器
            controller_count = _scan_module_for_controllers(module, module_name)

            # 缓存扫描结果
            _mark_module_scanned(module_name, controller_count)
            discovered_count += controller_count

            if controller_count > 0:
                logger.info(f"在 {module_name} 中发现 {controller_count} 个路由控制器")

        except Exception as e:
            logger.debug(f"处理文件 {file_path} 时出错: {e}")

    return discovered_count, skipped_count


def _scan_module_for_controllers(module, module_name):
    """
    扫描模块中的路由控制器

    Args:
        module: Python模块对象
        module_name (str): 模块名称

    Returns:
        int: 发现的控制器数量
    """
    controller_count = 0

    # 遍历模块中的所有属性
    for attr_name in dir(module):
        try:
            attr = getattr(module, attr_name)

            # 检查是否是类且有路由控制器标记
            if (isinstance(attr, type)
                    and hasattr(attr, '_is_route_controller')
                    and getattr(attr, '_is_route_controller')):
                controller_count += 1
                logger.debug(f"发现路由控制器: {module_name}.{attr_name}")

        except Exception as e:
            logger.debug(f"检查属性 {module_name}.{attr_name} 时出错: {e}")

    return controller_count


def autodiscover_with_pattern(pattern='**/views.py', exclude_patterns=None):
    """
    使用文件模式自动发现路由

    Args:
        pattern (str): 文件匹配模式
        exclude_patterns (list): 要排除的模式列表

    Returns:
        int: 发现的路由控制器类数量
    """
    import glob
    import fnmatch

    if exclude_patterns is None:
        exclude_patterns = ['**/migrations/**', '**/tests/**', '**/test_*.py']

    discovered_count = 0

    # 获取Django项目根目录
    base_dir = getattr(settings, 'BASE_DIR', os.getcwd())

    # 查找匹配的文件
    pattern_path = os.path.join(base_dir, pattern)
    matching_files = glob.glob(pattern_path, recursive=True)

    for file_path in matching_files:
        # 检查是否应该排除
        should_exclude = False
        for exclude_pattern in exclude_patterns:
            exclude_path = os.path.join(base_dir, exclude_pattern)
            if fnmatch.fnmatch(file_path, exclude_path):
                should_exclude = True
                break

        if should_exclude:
            continue

        try:
            # 将文件路径转换为模块名
            rel_path = os.path.relpath(file_path, base_dir)
            module_name = rel_path.replace(os.path.sep, '.').replace('.py', '')

            # 导入模块
            module = importlib.import_module(module_name)

            # 扫描控制器
            controller_count = _scan_module_for_controllers(module, module_name)
            discovered_count += controller_count

            if controller_count > 0:
                logger.info(f"在 {module_name} 中发现 {controller_count} 个路由控制器")

        except Exception as e:
            logger.debug(f"处理文件 {file_path} 时出错: {e}")

    return discovered_count


# 全局模块扫描缓存，避免重复导入
_scanned_modules = set()
_discovered_controllers = {}


def _is_module_scanned(module_name):
    """检查模块是否已被扫描"""
    return module_name in _scanned_modules


def _mark_module_scanned(module_name, controller_count):
    """标记模块已被扫描"""
    _scanned_modules.add(module_name)
    _discovered_controllers[module_name] = controller_count


def _get_cached_controller_count(module_name):
    """获取缓存的控制器数量"""
    return _discovered_controllers.get(module_name, 0)


def clear_discovery_cache():
    """清除发现缓存"""
    global _scanned_modules, _discovered_controllers
    _scanned_modules.clear()
    _discovered_controllers.clear()
    logger.info("已清除模块扫描缓存")


def smart_autodiscover():
    """
    智能自动发现路由

    结合多种策略进行路由发现，避免重复扫描：
    1. 扫描所有Django应用的常见模块
    2. 使用文件模式匹配（跳过已扫描的模块）
    3. 检查settings中的配置

    Returns:
        dict: 发现结果统计
    """
    results = {
        'app_scan_count': 0,
        'pattern_scan_count': 0,
        'total_count': 0,
        'skipped_modules': 0,
        'errors': []
    }

    try:
        # 1. 应用扫描
        logger.info("开始应用模式扫描...")
        app_count = autodiscover_routes(
            exclude_apps=['django.contrib.admin', 'django.contrib.auth',
                          'django.contrib.contenttypes', 'django.contrib.sessions',
                          'django.contrib.messages', 'django.contrib.staticfiles']
        )
        results['app_scan_count'] = app_count

        # 2. 文件模式扫描（跳过已扫描的模块）
        logger.info("开始文件模式扫描...")
        patterns = ['**/views.py', '**/controllers.py', '**/apis.py', '**/routes.py']
        pattern_count = 0
        skipped_count = 0

        for pattern in patterns:
            try:
                count, skipped = autodiscover_with_pattern_cached(pattern)
                pattern_count += count
                skipped_count += skipped
            except Exception as e:
                results['errors'].append(f"模式扫描错误 {pattern}: {e}")

        logger.info(f"文件模式自动发现完成，总共发现 {pattern_count} 个路由控制器")
        results['pattern_scan_count'] = pattern_count
        results['skipped_modules'] = skipped_count

        # 3. 检查settings配置
        custom_modules = getattr(settings, 'ROUTE_AUTODISCOVER_MODULES', [])
        if custom_modules:
            logger.info(f"扫描自定义模块: {custom_modules}")
            for module_name in custom_modules:
                try:
                    if _is_module_scanned(module_name):
                        logger.debug(f"跳过已扫描的自定义模块: {module_name}")
                        # results['app_scan_count'] += _get_cached_controller_count(module_name)
                        continue

                    module = importlib.import_module(module_name)
                    count = _scan_module_for_controllers(module, module_name)
                    _mark_module_scanned(module_name, count)
                    results['app_scan_count'] += count
                except Exception as e:
                    results['errors'].append(f"自定义模块扫描错误 {module_name}: {e}")

        results['total_count'] = results['app_scan_count'] + results['pattern_scan_count']

        if results['skipped_modules'] > 0:
            logger.debug(f"跳过了 {results['skipped_modules']} 个已扫描的模块，避免重复导入")

    except Exception as e:
        results['errors'].append(f"智能发现过程错误: {e}")

    return results


# Django应用就绪时自动发现路由的钩子
class RouteAutoDiscovery:
    """
    路由自动发现管理器
    """

    def __init__(self):
        self.discovered = False
        self.discovery_results = None

    def discover_if_needed(self):
        """
        如果还没有发现过，则进行自动发现
        """
        if not self.discovered:
            self.discovery_results = smart_autodiscover()
            self.discovered = True
            return self.discovery_results
        return self.discovery_results

    def force_rediscover(self):
        """
        强制重新发现（清除缓存）
        """
        clear_discovery_cache()  # 清除模块扫描缓存
        self.discovered = False
        return self.discover_if_needed()


# 全局自动发现管理器实例
auto_discovery = RouteAutoDiscovery()


# 便捷函数
def ensure_routes_discovered():
    """
    确保路由已被发现

    Returns:
        dict: 发现结果
    """
    return auto_discovery.discover_if_needed()


def force_rediscover_routes():
    """
    强制重新发现所有路由

    Returns:
        dict: 发现结果
    """
    return auto_discovery.force_rediscover()

# if __name__ == '__main__':
#     # 测试代码
#     print("Django路由自动发现测试")
#
#     # 模拟Django环境
#     import django
#     from django.conf import settings
#
#     if not settings.configured:
#         settings.configure(
#             DEBUG=True,
#             INSTALLED_APPS=[
#                 'django.contrib.contenttypes',
#                 'django.contrib.auth',
#                 'djangoapp.sample',
#                 'djangoapp.student',
#                 'djangoapp.webssh'
#             ],
#             SECRET_KEY='test-key'
#         )
#         django.setup()
#
#     # 执行自动发现
#     results = smart_autodiscover()
#     print(f"发现结果: {results}")
