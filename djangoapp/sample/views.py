from django.http import JsonResponse
import json

# Create your views here.


def make_response(code=200, data=None, message="操作成功！"):
    return JsonResponse({"code": code, "data": data, "message": message})


def sample(request):
    return make_response()
