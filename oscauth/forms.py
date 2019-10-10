# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import get_user_model

from project.pinnmodels import UmCurrentDeptManagersV

# from project import widgets

class AddUserForm(forms.Form):
    uniqname = forms.CharField(label='Uniqname', max_length=8)


class UserSuForm(forms.Form):

    username_field = get_user_model().USERNAME_FIELD

    user = forms.ModelChoiceField(
        label=_('Users'), queryset=get_user_model()._default_manager.order_by(
            username_field), required=True, widget=widgets.Select2Widget)  # pylint: disable=W0212

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



