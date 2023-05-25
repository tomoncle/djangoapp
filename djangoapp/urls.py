#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""djangoapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import re_path as url

from .common import page_not_found
from .common import paths
from .filestream.urls import file_patterns
from .sample.urls import sample_patterns
from .student.urls import student_patterns

# default url
urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

# function urls
urlpatterns += [
    url(r'^paths/$', paths),
]

# application urls
urlpatterns += file_patterns
urlpatterns += student_patterns
urlpatterns += sample_patterns

# handler config
handler404 = page_not_found
