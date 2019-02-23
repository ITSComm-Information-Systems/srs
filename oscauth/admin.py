from django.contrib import admin

# Register your models here.
from .models import Role
from .models import Privilege
from .models import Restriction
from .models import RolePrivilege
from .models import RolePrivRestriction

class RoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'display_seq_no', 'active', 'create_date', 'created_by',  'last_update_date', 'last_updated_by')
    ordering = ('display_seq_no', )

class PrivilegeAdmin(admin.ModelAdmin):
    list_display = ('privilege', 'display_seq_no', 'active', 'create_date', 'created_by',  'last_update_date', 'last_updated_by')
    ordering = ('display_seq_no', )

class RestrictionAdmin(admin.ModelAdmin):
    list_display = ('restriction', 'display_seq_no', 'active', 'create_date', 'created_by',  'last_update_date', 'last_updated_by')
    ordering = ('display_seq_no', )

class RolePrivilegeAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'privilege', 'active', 'create_date', 'created_by',  'last_update_date', 'last_updated_by')
    ordering = ('id', )
    search_fields = ('role__role', 'privilege__privilege')

class RolePrivRestrictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'privilege', 'restriction', 'active', 'create_date', 'created_by',  'last_update_date', 'last_updated_by')
    ordering = ('id', )
    search_fields = ('role__role', 'privilege__privilege', 'restriction__restriction', )

admin.site.register(Role, RoleAdmin)
admin.site.register(Privilege, PrivilegeAdmin)
admin.site.register(Restriction, RestrictionAdmin)
admin.site.register(RolePrivilege, RolePrivilegeAdmin)
admin.site.register(RolePrivRestriction, RolePrivRestrictionAdmin)