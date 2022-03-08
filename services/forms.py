from django import forms
from project.forms.fields import *
from .models import AWS, Azure, GCP
from project.integrations import MCommunity

# Defaults
CharField = forms.CharField( widget=forms.TextInput(attrs={'class': 'form-control'}) )
YesNo = forms.Select(choices=[('Yes','Yes',),('No','No',),] , attrs={'class': 'form-control col-2'})
NoYes = forms.Select(choices=[('No','No',),('Yes','Yes',),] , attrs={'class': 'form-control col-2'})


class CloudNewForm(forms.ModelForm):
    requestor = Uniqname(help_text='Please enter a valid uniqname.')
    #owner = McGroup(help_text="MCommunity Admin Group")  # TODO make this an admin group.
    #owner = forms.ChoiceField(choices=LDAPGroup.objects.all())
    acknowledge_sle = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'none'}))    
    acknowledge_srd = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'none'}))    

    contact_phone = forms.CharField()
    egress_waiver = forms.BooleanField(widget=NoYes)    
    sensitive_data_yn = forms.BooleanField(widget=NoYes)
    #non_regulated_data = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'class': 'none'}), choices=regdata)


    shortcode = forms.CharField(validators=[validate_shortcode])
    redhat = forms.BooleanField(label='Include RedHat OS?', widget=NoYes)
    vpn = forms.BooleanField(label='Do you require a VPN?', help_text='Choosing Yes will result in additional charges. Select Yes if you need access to resources on campus that are not available to the Internet, such as Active Directory.', widget=NoYes)
    request_consultation = forms.BooleanField(label='Request Consultation?', widget=NoYes)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user', None)

        super(CloudNewForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if hasattr(self.fields[field], 'widget'):
                if not self.fields[field].widget.attrs.get('class',None):
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


    def clean(self):
        super().clean()
        
        for err_field in self.errors:
            self.fields[err_field].widget.attrs['class'] += ' is-invalid'


class AwsNewForm(CloudNewForm):
    custom = ['mirate_existing','sensitive_data_yn','aws_email']
    skip = ['aws_account_number','acknowledge_srd','acknowledge_sle','regulated_data','non_regulated_data']

    migrate_existing = forms.BooleanField(label='Do you wish to bring an existing AWS account into the UM infrastructure?', widget=NoYes)
    aws_email = forms.CharField(help_text='What is the email address you registered with AWS?', label='')
    aws_account_number = forms.CharField(help_text='What is the AWS Account Number?', label='')
    aws_account_number.div_class = 'col-6'

    class Meta:
        model = AWS
        exclude = ['id','created_date','account_id','status','data_classification','version']
        widgets = {
            'billing_contact': forms.TextInput(attrs={'cols': 80, 'rows': 20}),
        }

    def __init__(self, *args, **kwargs):
        super(AwsNewForm, self).__init__(*args, **kwargs)
        self.fields['aws_account_number'].required = False
        self.fields['aws_email'].required = False

class AzureNewForm(CloudNewForm):
    redhat = None
    egress_waiver = None

    class Meta:
        model = Azure
        exclude = ['id','created_date','account_id','status']
        fields = ['requestor','owner','shortcode']
        widgets = {
            'billing_contact': forms.TextInput(attrs={'cols': 80, 'rows': 20}),
        }


class GcpNewForm(CloudNewForm):
    redhat = None

    class Meta:
        model = GCP
        exclude = ['id','created_date','account_id','status']
        widgets = {
            'billing_contact': forms.TextInput(attrs={'cols': 80, 'rows': 20}),
        }