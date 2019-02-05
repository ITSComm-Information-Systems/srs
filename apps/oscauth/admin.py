from django.contrib import admin

from .models import Role, Test

class RoleAdmin(admin.ModelAdmin):
    #model = Role
    list_display = ['role', 'role_desc']

class TestAdmin(admin.ModelAdmin):
    #model = Role
    list_display = ['name', 'descr']

admin.site.register(Role, RoleAdmin)
admin.site.register(Test, TestAdmin)

