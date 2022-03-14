from django import forms
from project.forms.fields import *
from .models import AWS, Azure, GCP
from project.integrations import MCommunity
from oscauth.models import LDAPGroup

# Defaults
CharField = forms.CharField( widget=forms.TextInput(attrs={'class': 'form-control'}) )
YesNo = forms.Select(choices=[('Yes','Yes',),('No','No',),] , attrs={'class': 'form-control col-2'})
NoYes = forms.Select(choices=[('No','No',),('Yes','Yes',),] , attrs={'class': 'form-control col-2'})


class CloudForm(forms.ModelForm):
    admin_group = forms.ChoiceField(help_text='MCommunity Admin Group')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user', None)

        super(CloudForm, self).__init__(*args, **kwargs)

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

            self.fields['admin_group'].choices = choice_list

        self.fields['admin_group'].initial = self.instance.owner

    def save(self):
        if 'admin_group' in self.changed_data:
            self.instance.owner = LDAPGroup().lookup( self.cleaned_data.get('admin_group') )

        super().save()

    def clean(self):
        super().clean()
        
        for err_field in self.errors:
            self.fields[err_field].widget.attrs['class'] += ' is-invalid'

class CloudNewForm(CloudForm):
    custom = ['sensitive_data_yn']
    skip = ['acknowledge_srd','acknowledge_sle','regulated_data','non_regulated_data']

    requestor = Uniqname(help_text='Please enter a valid uniqname.')

    acknowledge_sle = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'none'}))    
    acknowledge_srd = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'none'}))    

    contact_phone = forms.CharField()
    egress_waiver = forms.BooleanField(widget=NoYes)    
    sensitive_data_yn = forms.BooleanField(widget=NoYes)
    #non_regulated_data = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'class': 'none'}), choices=regdata)

    shortcode = forms.CharField(validators=[validate_shortcode])
    redhat = forms.BooleanField(label='Include RedHat OS?', widget=NoYes)
    vpn = forms.BooleanField(label='Do you require a VPN?'
        , help_text='Choosing Yes will result in additional charges. Select Yes if you need access to resources on campus that are not available to the Internet, such as Active Directory.'
        , widget=NoYes)
    request_consultation = forms.BooleanField(label='Request Consultation?', widget=NoYes)



AWS_REGION_CHOICES = [
    ('USEastNVA', 'US East (N. Virginia)'),
    ('USEastOH', 'US East (Ohio)'),
    ('USWestNCA', 'US West (N. California)'),
    ('USWestOR', 'US West (Oregon)'),
    ('APTokyo', 'Asia Pacific (Tokyo)'),
    ('APSeoul', 'Asia Pacific (Seoul)'),
    ('APMumbai', 'Asia Pacific (Mumbai)'),
    ('APSingapore', 'Asia Pacific (Singapore)'),
    ('APSydney', 'Asia Pacific (Sydney)'),
    ('Canada', 'Canada (Central)'),
    ('ChinaBejing', 'China (Beijing)'),
    ('ChinaNingxia', 'China (Ningxia)'),
    ('EUFrankfurt', 'EU (Frankfurt)'),
    ('EUIreland', 'EU (Ireland)'),
    ('EULondon', 'EU (London)'),
    ('EUParis', 'EU (Paris)'),
    ('SASaoPaulo', 'South America (Sao Paulo)')]

class AwsNewForm(CloudNewForm):
    title = 'ITS-Amazon Web Services at U-M Account Requests'
    custom = ['mirate_existing','sensitive_data_yn','aws_email']
    skip = ['aws_account_number','acknowledge_srd','acknowledge_sle','regulated_data','non_regulated_data']

    migrate_existing = forms.BooleanField(label='Do you wish to bring an existing AWS account into the UM infrastructure?', widget=NoYes)
    aws_email = forms.CharField(help_text='What is the email address you registered with AWS?', label='')
    aws_account_number = forms.CharField(help_text='What is the AWS Account Number?', label='')
    aws_account_number.div_class = 'col-6'

    region = forms.ChoiceField(label='Preferred Region',
        help_text='Some initial network scaffolding is constructed in the your preferred region. Other regions are also available within the account. If unsure leave the default.',
        choices=AWS_REGION_CHOICES)

    class Meta:
        model = AWS
        exclude = ['id','created_date','account_id','status','data_classification','version','owner']
        widgets = {
            'billing_contact': forms.TextInput(attrs={'cols': 80, 'rows': 20}),
        }

    def __init__(self, *args, **kwargs):
        super(AwsNewForm, self).__init__(*args, **kwargs)
        self.fields['aws_account_number'].required = False
        self.fields['aws_email'].required = False


class AzureNewForm(CloudNewForm):
    title = 'ITS-Microsoft Azure at U-M Account Requests'
    redhat = None
    egress_waiver = None

    class Meta:
        model = Azure
        exclude = ['id','created_date','account_id','status','owner']
        #fields = ['requestor','owner','shortcode']


class GcpNewForm(CloudNewForm):
    title = 'ITS-Google Cloud Platform at U-M Account Requests'
    custom = ['sensitive_data_yn','gcp_existing']
    skip = ['acknowledge_srd','acknowledge_sle','regulated_data','non_regulated_data','existing_id','existing_project','project_id']

    redhat = None


    #existing_yn = forms.BooleanField(label='Do you have an existing Google Project?',
    #    widget=forms.CheckboxInput(attrs={'data-toggle': 'collapse'}))  
    
    gcp_existing = forms.BooleanField(label='Do you have an existing Google Project?', widget=NoYes)
    existing_id = forms.CharField(label='Existing Project ID', required=False)
    existing_project = forms.CharField(label='Existing Project Name', required=False)

    #billing_yn
    #billing_id
    #billing_attach_project
    #billing_attach_id

    class Meta:
        model = GCP
        exclude = ['id','created_date','account_id','status','owner','project_id']


class AwsChangeForm(CloudForm):

    class Meta:
        model = AWS
        fields = ['shortcode','billing_contact','security_contact']

    
class AzureChangeForm(CloudForm):

    class Meta:
        model = Azure
        fields = ['shortcode','billing_contact','security_contact']


class GcpChangeForm(CloudForm):

    class Meta:
        model = GCP
        fields = ['admin_group','security_contact']
