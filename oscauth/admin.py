from django.contrib import admin

from .models import Role
from .models import AuthUserDept


class RoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'display_seq_no', 'active', 'create_date', 'last_update_date')
    ordering = ('display_seq_no', )


class AuthUserDeptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'group', 'dept')
    description = 'Users Authorized Departments'


admin.site.register(Role, RoleAdmin)
admin.site.register(AuthUserDept, AuthUserDeptAdmin)
