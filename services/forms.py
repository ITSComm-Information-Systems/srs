from django import forms
from project.forms.fields import *
from .models import AWS, Azure, GCP
from project.integrations import MCommunity
from oscauth.models import LDAPGroup

# Defaults
CharField = forms.CharField( widget=forms.TextInput(attrs={'class': 'form-control'}) )
YesNo = forms.Select(choices=[('Yes','Yes',),('No','No',),] , attrs={'class': 'form-control col-2'})
NoYes = forms.Select(choices=[('No','No',),('Yes','Yes',),] , attrs={'class': 'form-control col-2'})


NoYes = forms.Select(choices=[('No','No',),('Yes','Yes',),] , attrs={'class': 'form-control col-2'})


class AwsNewForm(forms.ModelForm):
    requestor = Uniqname(help_text='Please enter a valid uniqname.')
    #owner = McGroup(help_text="MCommunity Admin Group")  # TODO make this an admin group.
    #owner = forms.ChoiceField(choices=LDAPGroup.objects.all())

    #contact_phone = forms.CharField( widget=forms.TextInput(attrs={'class': 'form-control'}) )
    contact_phone = forms.CharField()


    shortcode = ShortCode()
    migrate = forms.BooleanField(label='Do you wish to bring an existing AWS account into the UM infrastructure?', widget=NoYes)

    redhat = forms.BooleanField(label='Include RedHat OS?', widget=NoYes)
    vpn = forms.BooleanField(label='Do you require a VPN?', help_text='Choosing Yes will result in additional charges. Select Yes if you need access to resources on campus that are not available to the Internet, such as Active Directory.', widget=NoYes)
    consult = forms.BooleanField(label='Request Consultation?', widget=NoYes)

    #Yes/No ask for 12 digit account number.

    class Meta:
        model = AWS
        exclude = ['id','created_date','account_id','status']
        widgets = {
            'billing_contact': forms.TextInput(attrs={'cols': 80, 'rows': 20}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user', None)

        super(AwsNewForm, self).__init__(*args, **kwargs)


        for field in self.fields:
            if hasattr(self.fields[field], 'widget'):
                print('widget', field)
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                print('no widget for', field)


        if self.user:
            group_list = MCommunity().get_groups(self.user.username)

            choice_list = [(None, '---')]
            for group in group_list:
                choice_list.append((group, group,))

            self.fields['owner'].choices = choice_list

            #if self.instance:
            #    self.fields['owner'].initial = self.instance.owner.name


class AzureNewForm(AwsNewForm):
    redhat = None

    class Meta:
        model = Azure
        exclude = ['id','created_date','account_id','status']
        widgets = {
            'billing_contact': forms.TextInput(attrs={'cols': 80, 'rows': 20}),
        }



class GcpNewForm(AwsNewForm):
    redhat = None

    class Meta:
        model = Azure
        exclude = ['id','created_date','account_id','status']
        widgets = {
            'billing_contact': forms.TextInput(attrs={'cols': 80, 'rows': 20}),
        }