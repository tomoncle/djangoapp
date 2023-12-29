#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from .models import Student, Clazz
from ..common import dict_filters
from ..common import ignore_self_waning


class ClassRestResponse(object):
    """
    views.func 函数中传入多少参数，method要传入对应数量的参数
    """

    @ignore_self_waning
    def get(self, _request, get_id=None):
        """
        http://localhost:8000/class/1?name=manth
        http://localhost:8000/class/?name=manth
        :return:
        """
        get_id = get_id or _request.GET.get('class_id')
        if get_id:
            data = Clazz.objects.filter(clazz_id=get_id)
            return data[0].to_dict() if data else None

        # 分页查询
        page = _request.GET.get('page', 1)  # 页码
        size = _request.GET.get("size", 10)  # 条目
        objects_list = Clazz.objects.all()
        paginator = Paginator(objects_list, size)
        page_obj = paginator.get_page(page)

        data = {
            'total': paginator.count,
            'current_page': int(page),
            'students': [s.to_dict() for s in page_obj.object_list]
        }
        return data

    @csrf_exempt
    def post(self, _request, *args):
        params = dict_filters(_request.POST, ['name', 'description'])
        obj = Clazz(**params)
        obj.save()
        return {'code': 200, 'data': obj.to_dict(), 'method': 'post'}


# Create your views here.
class StudentRestResponse(object):
    """
    views.func 函数中传入多少参数，method要传入对应数量的参数
    """

    @ignore_self_waning
    def get(self, _request, get_id=None):
        """
        http://localhost:8000/student/1?username=tom
        http://localhost:8000/student/?username=tom
        :return:
        """
        get_id = get_id or _request.GET.get('student_id')
        # 有ID就是查详情
        if get_id:
            data = Student.objects.filter(student_id=get_id)
            return data[0].to_dict() if data else None

        # 分页查询
        page = _request.GET.get('page', 1)  # 页码
        size = _request.GET.get("size", 10)  # 条目
        objects_list = Student.objects.all()
        paginator = Paginator(objects_list, size)
        page_obj = paginator.get_page(page)

        data = {
            'total': paginator.count,
            'current_page': int(page),
            'students': [s.to_dict() for s in page_obj.object_list]
        }
        return data

    @csrf_exempt
    def post(self, _request, *args):
        params = dict_filters(_request.POST, ['name', 'gender', 'age', 'clazz'])
        # clazz filed is ForeignKey object , clazz_id meaning the primary key of Clazz object.
        # "{filed}_id" meaning ForeignKey Object primary key.
        if params.get('clazz'):
            params['clazz_id'] = params.pop('clazz')
        obj = Student(**params)
        obj.save()
        return {'code': 200, 'data': obj.to_dict(), 'method': 'post'}

    @ignore_self_waning
    def put(self, _request, *args):
        params = _request.PUT
        student_id = params.get('student_id')
        name = params.get('name')
        obj, created = Student.objects.update_or_create(
            student_id=student_id,
            defaults={'name': name},
        )
        return obj.to_dict()

    @ignore_self_waning
    def delete(self, _request, del_id):
        del_id = del_id or _request.DELETE.get('student_id')
        Student.objects.filter(student_id=del_id).delete()
        return del_id

    @ignore_self_waning
    def head(self, _request, *args):
        """
        check request resources.
        :return None
        """
        assert _request

    @ignore_self_waning
    def patch(self, _request, *args):
        params = _request.PATCH
        student_id = params.get('student_id')
        name = params.get('name')
        obj, created = Student.objects.update_or_create(
            student_id=student_id,
            defaults={'name': name},
        )
        return obj.to_dict()


def student_index(request):
    """
    函数式接口，页面测试
    :param request:
    :return:
    """
    from django.shortcuts import render
    students = Student.objects.all()
    context = {'students': students}
    return render(request, 'students/index.html', context)


@csrf_exempt
def student_save(request):
    """
    函数式接口测试，直接返回Json
    :param request:
    :return:
    """
    from django.http import JsonResponse
    name = request.POST.get("name")
    stu = Student(name=name)
    stu.save()
    return JsonResponse({'data': stu.to_dict(), 'path': request.path, 'method': request.method})


def students_list(request):
    """
    函数式接口测试，直接返回Json
    :param request:
    :return:
    """
    from django.http import JsonResponse
    from django.core.paginator import Paginator

    page = request.GET.get('page', 1)
    size = request.GET.get("size", 10)
    objects_list = Student.objects.all()
    paginator = Paginator(objects_list, size)
    page_obj = paginator.get_page(page)

    data = {
        'total': paginator.count,
        'current_page': int(page),
        'students': [s.to_dict() for s in page_obj.object_list]
    }
    return JsonResponse({'data': data, 'path': request.path, 'method': request.method})
