from django.contrib import admin
from . import models
# Register your models here.
from django.utils.html import format_html
import uuid


# 自定义表的后台管理
@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    # 表格的表头,字段显示不能加多对多的字段
    list_display = ('name', 'description')
    # 可以修改的列表属性，修改字段，如果开启该属性，需要 list_display 添加显示 主键id
    # list_editable = ('platform', 'username', 'password', 'email')
    # 分页，显示数据的长度
    list_per_page = 10
    # 顶部查找
    search_fields = ('name', 'description',)
    # 右侧 filter
    list_filter = ('name', 'description',)
    # list_filter = (('platform', DropdownFilter), ('url', DropdownFilter), ('email', DropdownFilter),)
    # 排序
    ordering = ('name', 'group_id')


# 自定义表的后台管理
@admin.register(models.Server)
class ServerAdmin(admin.ModelAdmin):
    # 表格的表头,字段显示不能加多对多的字段
    list_display = ('name', 'auth', 'host', 'port', 'user', 'copy_pass', 'copy_key', 'webssh')
    # 可以修改的列表属性，修改字段，如果开启该属性，需要 list_display 添加显示 主键id
    # list_editable = ('platform', 'username', 'password', 'email')
    # 分页，显示数据的长度
    list_per_page = 10
    # 顶部查找
    search_fields = ('name', 'host',)
    # 右侧 filter
    list_filter = ('name', 'host',)
    # list_filter = (('platform', DropdownFilter), ('url', DropdownFilter), ('email', DropdownFilter),)
    # 排序
    ordering = ('name', 'server_id')

    def webssh(self, obj):
        _ = self
        if not obj.sid:
            return None
        return format_html("""<a href="/webssh/index?id={}&name={}" style="color:green" target="_blank">WEBSSH</a>""",
                           obj.sid, obj.name)

    webssh.short_description = "操作"

    def copy_key(self, obj):
        if not obj.secret_key:
            return None

        select_id = uuid.uuid1()
        return format_html("""
               <textarea id="{}" style="position: absolute; top: -10000px">{}</textarea>
               <a href="#" style="color:fuchsia" onclick="document.getElementById('{}').select(); 
               document.execCommand('copy'); 
               alert('已复制key')">复制密钥</a>""", select_id, obj.secret_key, select_id)

    copy_key.type = 'success'
    copy_key.short_description = '密钥'

    def copy_pass(self, obj):
        if not obj.password:
            return None

        select_id = uuid.uuid1()
        return format_html("""
               <input type="text" id="{}" value="{}" style="position: absolute; top: -10000px">
               <a href="#" style="color:red" onclick="document.getElementById('{}').select(); 
               document.execCommand('copy'); 
               alert('已复制')">复制密码</a>""", select_id, obj.password, select_id)

    copy_pass.type = 'success'
    copy_pass.short_description = '密码'
