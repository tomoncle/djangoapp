"""
Django settings for djangoapp project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
import platform
from pathlib import Path

# djangoapp config
if platform.system() == 'Windows':
    UPLOAD_DIR = 'D:/tmp/djangoapp'
else:
    UPLOAD_DIR = '/tmp/djangoapp'
if not os.path.exists(UPLOAD_DIR) or not os.path.isdir(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-74a&qk)9pa(+v(n_k^_!natt&vk!_bv27vlqe=ppie#5*^=69j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
# 项目模块
PROJECT_APPS = [
    'channels',
    'djangoapp.sample',
    'djangoapp.student',
    'djangoapp.webssh'
]
# 模块集成
INSTALLED_APPS.extend(PROJECT_APPS)

# 配置 discover_routes 自动发现选项（可选）
# 指定要扫描的自定义模块
# ROUTE_AUTODISCOVER_MODULES = [
#     'myapp.controllers',
#     'api.views',
#     'custom.routes',
# ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'djangoapp.common.HttpMiddleware'
]

ROOT_URLCONF = 'djangoapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# websocket 配置
ASGI_APPLICATION = 'djangoapp.asgi.application'

WSGI_APPLICATION = 'djangoapp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-Hans'

# 配置使用 北京时间
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

# 配置 False 为启用 TIME_ZONE 规定的时区，如果为True，则使用 UTC 时间
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# STATIC_URL = 'static/'
# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
# 静态资源文件夹路径,必须有"/"为前缀
STATIC_ROOT = '/static/'
# 在html中引用时的前缀,必须有"/"为前缀
STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# @login_required
LOGIN_URL = '/admin/login'

# loguru Logger Level
os.environ['LOGURU_LEVEL'] = 'TRACE'
