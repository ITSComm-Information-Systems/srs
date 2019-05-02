from django.contrib import admin

from .models import Role
from .models import Grantor
from .models import AuthUserDept


class RoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'display_seq_no', 'active', 'create_date', 'last_update_date')
    ordering = ('display_seq_no', )


class AuthUserDeptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'group', 'dept')
    description = 'Users Authorized Departments'
    search_fields = ['user__username', 'group__name', 'dept', ]


class GrantorAdmin(admin.ModelAdmin):
    list_display = ('id', 'grantor_role', 'granted_role', 'display_seq_no')
    description = 'Roles Authorized to Grant Access'
    ordering = ('display_seq_no', )
    search_fields = ['grantor_role__name', 'granted_role__role',]

admin.site.register(Role, RoleAdmin)
admin.site.register(AuthUserDept, AuthUserDeptAdmin)
admin.site.register(Grantor, GrantorAdmin)
