from django.contrib import admin

from .models import Role
from .models import Grantor
from .models import AuthUserDept
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, connections

from django.urls import path

from django.template.response import TemplateResponse
from django import forms
from project.forms.fields import Uniqname
from project.pinnmodels import UmMpathDwCurrDepartment

from django.template.loader import render_to_string
from django.contrib.auth.admin import UserAdmin

# Unregister the default User admin
admin.site.unregister(User)

class CustomUserAdmin(UserAdmin):

    @admin.display(description='Permissions')
    def custom_permissions(self, obj):
        if not obj or not obj.username:
            return 'None'

        CUSTOM_PERMISSIONS = (
            ('bom.can_access_bom', 'PS_RATING.UM_RTE_TECHNICIAN_V.UNIQNAME'),
            ('rte.add_umrteinput', 'PS_RATING.UM_RTE_TECHNICIAN_V.UNIQNAME'),
            ('rte.add_submitalltechs', 'SRS RTE Admin Group'),
            ('oscauth.can_report_all', 'SRS Project Managers Group'),
            ('bom.can_update_bom_ordered', 'UM_BOM_PROCUREMENT_USERS_V'),
        )

        permissions = [
            {
                'name': name,
                'granted': obj.has_perm(name),
                'source': source,
            }
            for name, source in CUSTOM_PERMISSIONS
        ]

        return render_to_string('admin/auth/user/custom_permissions.html',
            {'permissions': permissions, 'user': obj},)

    readonly_fields = (*UserAdmin.readonly_fields,'custom_permissions',)

    fieldsets = UserAdmin.fieldsets + (
        (
            'Custom Permissions',
            {
                'fields': ('custom_permissions',),
            },
        ),
    )

admin.site.register(User, CustomUserAdmin)



class RoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'display_seq_no', 'active', 'create_date', 'last_update_date')
    ordering = ('display_seq_no', )


class BulkUpdateForm(forms.Form):
    department_group = forms.MultipleChoiceField(choices=())  # placeholder
    uniqname = Uniqname(max_length=8)
    role = forms.ChoiceField(choices=[('','----'),('4','Proxy'),('5','Orderer'),('6','Reporter')])
    action = forms.ChoiceField(choices=[('','----'),('Add','Add'),('Delet','Delete')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        vp_groups = (
            UmMpathDwCurrDepartment.objects
            .exclude(dept_grp=' ')
            .values_list('dept_grp', 'dept_grp_descr')
            .distinct()
            .order_by('dept_grp_descr')
        )

        self.fields["department_group"].choices = vp_groups

    def clean(self):
        try:
            self.user = User.objects.get(username=self.cleaned_data.get('uniqname'))
        except ObjectDoesNotExist:
            self.add_error('uniqname', 'User not found in SRS.')

        super().clean()

class AuthUserDeptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'group', 'dept')
    description = 'Users Authorized Departments'
    search_fields = ['user__username', 'group__name', 'dept', ]

    def get_urls(self):
        urls = super().get_urls()

        bulk_update = [
            path('bulk_update/', self.bulk_update),
        ]

        return bulk_update + urls

    def bulk_update(self, request):
        context = self.admin_site.each_context(request)
        context['title'] = 'Bulk Update'
        context['form'] = BulkUpdateForm()

        if request.method == 'POST':
            form = BulkUpdateForm(request.POST)

            if form.is_valid():
                action = form.cleaned_data['action']
                group_id = form.cleaned_data['role']
                department_group = form.cleaned_data['department_group']

                dept_list = list(UmMpathDwCurrDepartment.objects.filter(dept_grp__in=department_group).values_list('deptid', flat=True).distinct())

                count = 0
                if form.cleaned_data['action'] == 'Add':
                    for dept in dept_list:
                        rec = AuthUserDept()
                        rec.user = form.user
                        rec.group_id = group_id
                        rec.dept = dept

                        try:
                            rec.save()
                            count += 1
                        except:
                            print('Unique Constraint')
                else:
                    result = AuthUserDept.objects.filter(dept__in=dept_list, user=form.user, group_id=group_id).delete()
                    count = result[0]

                context['message'] = f'{count} records {action}ed'
          
            else:
                context['form'] = form

        return TemplateResponse(
            request,
            'admin/oscauth/authuserdept/bulk_update.html',
            context,
        )

class GrantorAdmin(admin.ModelAdmin):
    list_display = ('id', 'grantor_role', 'granted_role', 'display_seq_no')
    description = 'Roles Authorized to Grant Access'
    ordering = ('display_seq_no', )
    search_fields = ['grantor_role__name', 'granted_role__role',]

admin.site.register(Role, RoleAdmin)
admin.site.register(AuthUserDept, AuthUserDeptAdmin)
admin.site.register(Grantor, GrantorAdmin)
