  
# -*- coding: utf-8 -*-
from django import forms
#from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
#from django.forms.fields import EMPTY_VALUES
#from django.utils.translation import ugettext_lazy as _
from project.pinnmodels import UmOscAllActiveAcctNbrsV
from oscauth.utils import get_mc_group


from django.core.exceptions import ValidationError


class ShortCode(forms.CharField):
    template_name = 'project/text.html'
    widget=forms.TextInput(attrs={'class': 'form-control'})

    def validate(self, value):

        try:
            UmOscAllActiveAcctNbrsV.objects.get(short_code=value)
        except:
            self.widget.attrs.update({'class': 'form-control is-invalid'})
            raise ValidationError('That is not a valid shortcode', code='shortcode')


class McGroup(forms.CharField):
    #widget = forms.EmailInput
    #default_validators = [validators.validate_email]
    template_name = 'project/text.html'

    widget=forms.TextInput(attrs={'class': 'form-control'})

    def validate(self, value):

        if not get_mc_group(value):
            self.widget.attrs.update({'class': 'form-control is-invalid'})
            raise ValidationError('That is not a valid group in MCommunity', code='mcgroup')



