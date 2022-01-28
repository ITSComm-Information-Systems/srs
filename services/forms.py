from django import forms
from project.forms.fields import *

# Defaults
CharField = forms.CharField( widget=forms.TextInput(attrs={'class': 'form-control'}) )
YesNo = forms.Select(choices=[('Yes','Yes',),('No','No',),] , attrs={'class': 'form-control col-2'})
NoYes = forms.Select(choices=[('No','No',),('Yes','Yes',),] , attrs={'class': 'form-control col-2'})


NoYes = forms.Select(choices=[('No','No',),('Yes','Yes',),] , attrs={'class': 'form-control col-2'})


class AwsNewForm(forms.Form):
    requestor = Uniqname(help_text='Please enter a valid uniqname.')
    owner_group = McGroup(help_text="MCommunity Admin Group")  # TODO make this an admin group.
    contact_phone = forms.CharField( widget=forms.TextInput(attrs={'class': 'form-control'}) )
    short_code = ShortCode()
    migrate = forms.BooleanField(label='Do you wish to bring an existing AWS account into the UM infrastructure?', widget=NoYes)

    redhat = forms.BooleanField(label='Include RedHat OS?', widget=NoYes)
    vpn = forms.BooleanField(label='Do you require a VPN?', help_text='Choosing Yes will result in additional charges. Select Yes if you need access to resources on campus that are not available to the Internet, such as Active Directory.', widget=NoYes)
    consult = forms.BooleanField(label='Request Consultation?', widget=NoYes)

    #Yes/No ask for 12 digit account number.