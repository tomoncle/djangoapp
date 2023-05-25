# Register your models here.
from django.contrib import admin

from .models import Sample


@admin.register(Sample)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('sam_id', 'name', 'description', 'create_time')  # 显示属性并排序
    list_filter = ('create_time',)  # 查询条件
