"""
URL configuration for djangoapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from .common import page_not_found
from .common import register_routes
from .filestream.urls import file_patterns
from .student.urls import student_patterns
from .webssh.urls import webssh_patterns

# default url
urlpatterns = [
    path('admin/', admin.site.urls),
              ] + register_routes()

# application urls
urlpatterns += student_patterns
urlpatterns += file_patterns
urlpatterns += webssh_patterns

# handler config
handler404 = page_not_found
