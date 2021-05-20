from django.contrib import admin

from .models import Role
from .models import Grantor
from .models import AuthUserDept
from django.contrib.auth.models import User
from django.db import IntegrityError

from django.urls import path

from django.template.response import TemplateResponse
from django import forms
from project.forms.fields import Uniqname
from project.pinnmodels import UmOscDeptUnitsReptV

class RoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'display_seq_no', 'active', 'create_date', 'last_update_date')
    ordering = ('display_seq_no', )


class BulkUpdateForm(forms.Form):
    groups_descr = UmOscDeptUnitsReptV.objects.order_by('dept_grp_descr').values_list('dept_grp', 'dept_grp_descr').distinct()

    department_group = forms.ChoiceField(choices=groups_descr)
    uniqname = Uniqname(max_length=8)
    role = forms.ChoiceField(choices=[('','----'),('4','Proxy'),('5','Orderer'),('6','Reporter')])
    action = forms.ChoiceField(choices=[('','----'),('Add','Add'),('Delet','Delete')])


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
                uniqname = form.cleaned_data['uniqname']
                action = form.cleaned_data['action']
                group_id = form.cleaned_data['role']

                department_group = form.cleaned_data['department_group']
                dept_list = list(UmOscDeptUnitsReptV.objects.filter(dept_grp=department_group).values('deptid').distinct())

                user = User.objects.get(username=uniqname)
                count = 0

                for dept in dept_list:
                    if form.cleaned_data['action'] == 'Add':
                        rec = AuthUserDept()
                        rec.user = user
                        rec.group_id = group_id
                        rec.dept = dept['deptid']
                        try:
                            rec.save()
                            count += 1
                        except IntegrityError:
                            print('Not added, already exists')
                    else:
                        AuthUserDept.objects.filter(dept=dept['deptid'], user=user, group_id=group_id).delete()
                        count += 1

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
