from django import forms
from project.pinnmodels import UmOscAllActiveAcctNbrsV, UmOscServiceProfileV
from oscauth.utils import get_mc_group, get_mc_user
from oscauth.models import AuthUserDept

from project.models import validate_shortcode

from django.core.exceptions import ValidationError


class Phone(forms.CharField):
    template_name = 'project/text.html'
    widget=forms.TextInput(attrs={'class': 'form-control'})

    def validate(self, value):
        value = value.replace('-','')
        locations = list(UmOscServiceProfileV.objects.filter(service_number=value).exclude(location_id=0).values())

        if locations:
            authorized_departments = AuthUserDept.get_order_departments(self.current_user)
            phone_dept = locations[0]['deptid']
            authorized = False

            for dept in authorized_departments:
                if dept.dept == phone_dept:
                    authorized = True

            if authorized:
                return
            else:
                self.widget.attrs.update({'class': 'form-control is-invalid'})
                raise ValidationError(f'You are not authorized for department {phone_dept}', code='shortcode')
        else:
            self.widget.attrs.update({'class': 'form-control is-invalid'})
            raise ValidationError('That is not a valid Phone Number', code='shortcode')


class Uniqname(forms.CharField):

    template_name = 'project/text.html'
    widget=forms.TextInput(attrs={'class': 'form-control'})

    def validate(self, value):
        if not value and not self.required:
            return

        user = get_mc_user(value)
        if user:
            return
        else:
            self.widget.attrs.update({'class': 'form-control is-invalid'})
            raise ValidationError('That is not a valid uniqname', code='shortcode')


class ShortCode(forms.CharField):
    template_name = 'project/text.html'
    widget=forms.TextInput(attrs={'class': 'form-control'})
    #validators=[validate_shortcode]

    #def validate(self, value):

     #   try:
     #       UmOscAllActiveAcctNbrsV.objects.get(short_code=value)
     #   except:
     #       self.widget.attrs.update({'class': 'form-control is-invalid'})
     #       raise ValidationError('That is not a valid shortcode', code='shortcode')


class McGroup(forms.CharField):
    #widget = forms.EmailInput
    #default_validators = [validators.validate_email]
    template_name = 'project/text.html'

    widget=forms.TextInput(attrs={'class': 'form-control'})

    def validate(self, value):

        if not get_mc_group(value):
            self.widget.attrs.update({'class': 'form-control is-invalid'})
            raise ValidationError('That is not a valid group in MCommunity', code='mcgroup')



