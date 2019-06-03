# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import get_user_model

from project.pinnmodels import UmCurrentDeptManagersV

from dal import autocomplete
from django_select2.forms import Select2MultipleWidget, Select2Widget, ModelSelect2Widget, ModelSelect2MultipleWidget

class AddUserForm(forms.Form):
    uniqname = forms.CharField(label='Uniqname', max_length=8)


class UserSuForm(forms.Form):

    username_field = get_user_model().USERNAME_FIELD

    user = forms.ModelChoiceField(
        label=_('Users'), queryset=get_user_model()._default_manager.order_by(
            username_field), required=True)  # pylint: disable=W0212

    use_ajax_select = False

    def __init__(self, *args, **kwargs):
        super(UserSuForm, self).__init__(*args, **kwargs)

        if 'ajax_select' in settings.INSTALLED_APPS and getattr(
                settings, 'AJAX_LOOKUP_CHANNELS', None):
            from ajax_select.fields import AutoCompleteSelectField

            lookup = settings.AJAX_LOOKUP_CHANNELS.get('oscauth', None)
            if lookup is not None:
                old_field = self.fields['user']

                self.fields['user'] = AutoCompleteSelectField(
                    'oscauth',
                    required=old_field.required,
                    label=old_field.label,
                )
                self.use_ajax_select = True

    def get_user(self):
        return self.cleaned_data.get('user', None)

    def __str__(self):
        if 'formadmin' in settings.INSTALLED_APPS:
            try:
                from formadmin.forms import as_django_admin
                return as_django_admin(self)
            except ImportError:
                pass
        return super(UserSuForm, self).__str__()

class DeptForm(forms.Form):
    query = UmCurrentDeptManagersV.objects.all().order_by('deptid')

    DEPT_CHOICES = [tuple([q.deptid, q.deptid]) for q in query]

    deptids = forms.ChoiceField(label='Department ID', choices=DEPT_CHOICES, widget=Select2Widget(attrs={'data-placeholder': '--Select--', 'data-width': '15%'}))
    # deptids = forms.CharField(label='Department ID', widget=Select2Widget(choices=DEPT_CHOICES), initial='--Select--')
    # deptids = forms.ModelChoiceField(queryset=UmCurrentDeptManagersV.objects.all().order_by('deptid'))#, widget=Select2MultipleWidget)

    # class Meta:
    #     widgets = {
    #         'deptids': Select2Widget
    #     }
    #     model = UmCurrentDeptManagersV
    #     fields = ['deptid']
    #     widgets = {
    #         'deptids':autocomplete.TextWidget('DeptAutocomplete')
    #     }

# class DeptForm(forms.ModelForm):
#     #deptids = forms.ModelMultipleChoiceField(queryset=UmCurrentDeptManagersV.objects.all().order_by('deptid'), widget=Select2Widget)

#     class Meta:
#         model = UmCurrentDeptManagersV
#         fields = ('deptid', )
#         widgets = {
#             'deptid': Select2Widget(
#                 attrs={'data-placeholder': '--Select--', 'data-width': '100%'},)
#         }

# class DeptForm(forms.ModelForm):
#     deptids = forms.ModelChoiceField(
#         queryset=UmCurrentDeptManagersV.objects.values_list('deptid').all().order_by('deptid'),
#         label='Department ID',
#         widget=ModelSelect2Widget(
#             model=UmCurrentDeptManagersV,
#             search_fields=['deptid__icontains'],
#             attrs={'data-placeholder': '--Select--', 'data-width': '100%'},),)

#     class Meta():
#         model = UmCurrentDeptManagersV
#         fields = ('deptid',)

# class DeptForm(forms.Form):
#     ids = forms.ModelMultipleChoiceField(queryset=UmCurrentDeptManagersV.objects.values('deptid').all().order_by('deptid'),
#         widget=ModelSelect2MultipleWidget(queryset=UmCurrentDeptManagersV.objects.values('deptid').all().order_by('deptid'),
#         search_fields=['ids__icontains']))
