from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    server_id = request.GET.get("id")
    name = request.GET.get("name")
    context = {'connect': {'id': server_id, 'name': name}}
    return render(request, "webssh/index.html", context)
