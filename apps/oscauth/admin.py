from django.contrib import admin

from .models import Role

class RoleAdmin(admin.ModelAdmin):
    #model = Role
    list_display = ['role', 'role_description','is_dept_manager','can_add_proxy',
                   'can_add_nonproxy_users','can_submit_orders','can_run_reports']

admin.site.register(Role, RoleAdmin)

