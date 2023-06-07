#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt

from .models import Student,Clazz
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
        return [s.to_dict() for s in Student.objects.all()]

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
        if get_id:
            data = Student.objects.filter(student_id=get_id)
            return data[0].to_dict() if data else None
        return [s.to_dict() for s in Student.objects.all()]

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
    from django.shortcuts import render
    students = Student.objects.all()
    context = {'students': students}
    return render(request, 'students/index.html', context)
