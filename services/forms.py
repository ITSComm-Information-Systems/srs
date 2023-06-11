from django import forms
from django.core import validators
from project.forms.fields import *
from .models import AWS, Azure, GCP, GCPAccount, Container, CloudDesktop, CloudImage
from project.integrations import MCommunity, Openshift
from oscauth.models import LDAPGroup, LDAPGroupMember
from .clouddesktopchoices import CPU_CHOICES,RAM_CHOICES,STORAGE_CHOICES

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
        cleaned_data = super().clean()
        
        for err_field in self.errors:
            self.fields[err_field].widget.attrs['class'] += ' is-invalid'

        return cleaned_data

class CloudNewForm(CloudForm):
    custom = ['sensitive_data_yn']
    skip = ['acknowledge_srd','acknowledge_sle','regulated_data','non_regulated_data']

    requestor = Uniqname(help_text='Please enter a valid uniqname.')
    billing_contact = Uniqname(help_text='Please enter a valid uniqname.')
    security_contact = Uniqname(help_text='Please enter a valid uniqname.')

    acknowledge_sle = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'none'}))    
    acknowledge_srd = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'none'}))    

    contact_phone = forms.CharField()
    egress_waiver = forms.BooleanField(widget=YesNo)    
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
    custom = ['sensitive_data_yn','vpn_tier']
    skip = ['acknowledge_srd','acknowledge_sle','regulated_data','non_regulated_data','vpn']
    redhat = None
    egress_waiver = None
    request_consultation = None

    class Meta:
        model = Azure
        exclude = ['id','created_date','account_id','status','owner','name']
        #fields = ['requestor','owner','shortcode']


class GcpNewForm(CloudNewForm):
    title = 'ITS-Google Cloud Platform at U-M Account Requests'
    custom = ['sensitive_data_yn','gcp_existing','nih_yn']
    skip = ['acknowledge_srd','acknowledge_sle','regulated_data','non_regulated_data','existing_id','existing_project','project_id'
            ,'nih_id','nih_officer_name','nih_officer_email']


    nih_yn = forms.BooleanField(label='Have you been awarded NIH STRIDES funding?', widget=NoYes)
    nih_id = forms.CharField(label='NIH Award/Project/Application ID', required=False)
    nih_officer_name = forms.CharField(label='NIH Program Officer Name', required=False)
    nih_officer_email = forms.CharField(label='NIH Program Officer Email', required=False)

    
    gcp_existing = forms.BooleanField(label='Do you have an existing Google Project?',
                                       help_text='Are you migrating an existing project into MCloud?', widget=NoYes)
    existing_id = forms.CharField(label='Existing Project ID', required=False)
    existing_project = forms.CharField(label='Existing Project Name', required=False)
    network = forms.BooleanField(label='Do you require a network?', widget=NoYes)

    def __init__(self, *args, **kwargs):
        super(GcpNewForm, self).__init__(*args, **kwargs)

        if self.user:
            groups = list(LDAPGroupMember.objects.filter(username=self.user).values_list('ldap_group_id'))
            account_list = GCPAccount.objects.filter(status='A',owner__in=groups).distinct().values('id','account_id')

            choice_list = []
            for account in account_list:
                choice_list.append((account['id'], account['account_id'],))
                self.fields['gcp_account'].initial = account['id']

            choice_list.append((None, 'New'))

            self.fields['gcp_account'].choices = choice_list
            self.fields['gcp_account'].required = False
            self.fields['gcp_account'].label = 'GCP Billing Account'

    class Meta:
        model = GCP
        exclude = ['id','created_date','account_id','status','owner','project_id']

    field_order = ['requestor','nih_yn','gcp_account','gcp_existing']

    def save(self, *args, **kwargs):
        if self.instance.gcp_account_id == None:
            acct = GCPAccount()
            acct.shortcode = self.cleaned_data.get('shortcode')
            acct.billing_contact = self.cleaned_data.get('billing_contact')
            acct.owner = self.cleaned_data.get('owner')
            acct.save()
            self.instance.gcp_account_id = acct.id

        super().save(*args, **kwargs)  # Call the "real" save() method.


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


class GcpaccountChangeForm(CloudForm):

    class Meta:
        model = GCPAccount
        fields = ['owner','shortcode']


def validate_project_name(value):
    if Openshift().get_project(value).ok:
        raise ValidationError(f'A project with this name already exists.  Please select a different name.')
    

class ContainerNewForm(CloudForm):
    title = 'Request a Container Service Project'
    custom = ['database_type', 'course_info']
    skip = ['acknowledge_srd','acknowledge_sle','regulated_data','non_regulated_data','container_sensitive']
    container_sensitive = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'none'}))    
    course_yn = forms.BooleanField(widget=NoYes,
        label='Are you requesting this service for a course project?',
        help_text = "This service is available at no cost for faculty, staff, or students provided it's being used for a project or activity associated with a current U-M course. Faculty may request multiple application instances at one time (e.g., one per student). A valid course code is required.")
    course_info = forms.CharField(required=False)
    shortcode = forms.CharField(validators=[validate_shortcode], required=False)
    admin_group = forms.ChoiceField(label='Contact Group', help_text='The MCommunity group is used to identify a point of contact should the primary point of contact for this account change. Must be public and contain at least 2 members. The MCommunity group will not be used to define or maintain access to your project. Please omit @umich.edu from your group name in this field.')
    project_name = forms.CharField(help_text='The project name is a unique identifier used for billing purposes and to generate your unpublished URL (project-name.webplatformsunpublished.umich.edu). Must be lowercase, contain no special characters, and contain no spaces. Hyphens are permitted.',
                                   validators=[validators.RegexValidator(
                                        regex='^[a-z0-9][0-9a-z\-]*[a-z0-9]$',  # lowercase and hypens, also start and end with a lowercase letter
                                        message="Label must consist of lower case alphanumeric characters or '-', and must start and end with an alphanumeric character.",
                                        code='invalid_name'), validate_project_name]
                                   )

    project_description = forms.CharField(required=False, help_text='Used to describe any charges associated with this project on billing invoices.')
    backup = forms.CharField(widget=NoYes, help_text='Selecting "Yes" here will automatically create a backup of the artifacts and persistent volumes associated with your application.')
    admins = forms.CharField(widget=forms.Textarea(attrs={"rows":2}), help_text='List uniqnames of users who should be "Admins" for this project.  Enter one uniqname per line.')
    editors = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows":2}), help_text='List uniqnames of users who should have "Edit" access to this project.  Enter one uniqname per line.')
    viewers = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows":2}), help_text='List uniqnames of users who should have "View" access to this project.  Enter one uniqname per line.')

    class Meta:
        model = Container
        fields = ['container_sensitive','admin_group','course_yn','course_info','shortcode',
                  'project_name', 'project_description', 'size','database','database_type','backup'] # Remaining follow form order

    def clean(self):
        # Check all uniqnames in a single call for efficiency porpoises
        uniqnames = []
        cleaned_names = {}
        for users in ['admins', 'editors', 'viewers']:
            cleaned_names[users] = []
            for user in self.cleaned_data.get(users).split('\n'):
                user = user.strip('\r, ')
                uniqnames.append(user)
                cleaned_names[users].append(user)

        valid_uniqnames = MCommunity().check_user_list(uniqnames)

        for users in ['admins', 'editors', 'viewers']:
            error = ''
            for user in cleaned_names[users]:
                if user and user not in valid_uniqnames:
                    error = error + user + ' '
            
            if error:
                self.add_error(users, error + 'not found.')        

        self.instance.cleaned_names = cleaned_names  # Hang on to this for later.

        return super().clean()

    def save(self):
        # Create project in openshift, don't save to SRS.
        os = Openshift()
        os.create_project(self.instance, self.user.username)


ACCESS_INTERNET_CHOICES = (('True','Yes, my desktop needs internet access (outside of U of M sites)'),('False','No, my desktop do not need internet access to any network outside of U of M'))
class ClouddesktopNewForm(CloudForm):
    MASK_CHOICES = [["/28", "/28 (16 addresses)"], ["/27", "/27 (32 addresses)"], ["/26", "/26 (64 addresses)"], 
                    ["/25", "/25 (128 addresses)"], ["/24", "/24 (256 addresses)"]]
    
    CPU_INITIAL = 1.15
    MEMORY_INITIAL = 0.96
    STORAGE_INITIAL = 5.00
    GPU_INITIAL = 0.00
    BASE_COST = 31.31
    TOTAL_INITIAL = CPU_INITIAL + MEMORY_INITIAL + STORAGE_INITIAL + GPU_INITIAL + BASE_COST

    title = 'MiDesktop New Order Form'
    shared_network = forms.ChoiceField(choices=((True, 'Shared Network'), (False, 'New Dedicated Network')))
    initial_image = forms.ChoiceField(choices=(('Blank','Blank Image'),('Standard','MiDesktop Standard Image')))
    operating_system = forms.ChoiceField(choices=(('Windows10 64bit','Windows10 64bit'),))

    purpose = forms.CharField(required=False)

    base_image_name = forms.CharField()
    cpu = forms.ChoiceField(choices=CPU_CHOICES)
    cpu_cost = forms.DecimalField(initial=CPU_INITIAL)
    memory = forms.ChoiceField(choices=RAM_CHOICES)
    memory_cost = forms.DecimalField(initial=MEMORY_INITIAL)
    storage = forms.ChoiceField(choices=STORAGE_CHOICES)
    storage_cost = forms.DecimalField(initial=STORAGE_INITIAL)
    gpu = forms.ChoiceField(choices=((True,'Yes'),(False,'No')), widget=forms.Select(), initial=False, label="GPU(optional)")
    gpu_cost = forms.DecimalField(initial=GPU_INITIAL)
    total = forms.DecimalField(initial=TOTAL_INITIAL)
    pool_name = forms.CharField()
    auto_logout = forms.ChoiceField(choices=(('Never','Never'),('Immediately','Immediately'),('[Custom]','[Custom]')))
    pool_maximum = forms.IntegerField()
    powered_on_desktops = forms.IntegerField() 
    min_desktops = forms.IntegerField()
    ad_container = forms.CharField()
    ad_groups = forms.CharField()
    additional_details = forms.CharField(required=False)
    access_internet = forms.ChoiceField(required=False,choices=ACCESS_INTERNET_CHOICES)
    mask = forms.ChoiceField(choices=MASK_CHOICES, required=False)
    protection = forms.ChoiceField(choices=((True,'Yes'),(False,'No')), widget=forms.Select(), initial=False, required=False)
    technical_contact = forms.CharField(required=False)
    billing_contact = forms.CharField(required=False)
    security_contact = forms.CharField(required=False)


    def save(self):
        # Save the form data to create a new pool instance
        image_name=self.cleaned_data['base_image_name']
        owner = LDAPGroup().lookup( self.cleaned_data.get('admin_group') )
        cpu=self.cleaned_data['cpu']
        gpu=self.cleaned_data['gpu']
        storage=self.cleaned_data['storage']
        memory=self.cleaned_data['memory']
        cpu_cost = self.cleaned_data['cpu_cost']
        storage_cost = self.cleaned_data['storage_cost']
        memory_cost = self.cleaned_data['memory_cost']
        gpu_cost = self.cleaned_data['gpu_cost']
        total = self.cleaned_data['total']
        pool_name = self.cleaned_data['pool_name']
        pool_maximum = self.cleaned_data['pool_maximum']
        pool_cost = int(pool_maximum) * total
        ad_access_groups = self.cleaned_data['ad_groups']
        sla = self.cleaned_data['sla']
        shortcode = self.cleaned_data['shortcode']
        shared_network = self.cleaned_data['shared_network']
        if shared_network == 'False':
            access_internet = True
            mask = self.cleaned_data['mask']
            protection = self.cleaned_data['protection']
            technical_contact = self.cleaned_data['technical_contact']
            billing_contact = self.cleaned_data['billing_contact']
            security_contact = self.cleaned_data['security_contact']
        else:
            access_internet = False
            mask = ''
            protection = False
            technical_contact = ''
            billing_contact = ''
            security_contact = ''


        image = CloudImage(
            owner=owner,
            account_id=image_name,
            shortcode = shortcode,
            cpu=cpu,
            cpu_cost=cpu_cost,
            memory=memory,
            memory_cost=memory_cost,
            storage=storage,
            storage_cost = storage_cost,
            gpu=gpu,
            gpu_cost=gpu_cost,
            total = total,
            shared_network = shared_network
        )

        image.save()

        pool = CloudDesktop(
            owner=owner,
            account_id = pool_name,
            shortcode = shortcode,
            pool_maximum = pool_maximum,
            pool_cost = pool_cost,
            ad_access_groups = ad_access_groups,
            sla=sla,
            image_id = image.id,
            access_internet = access_internet,
            mask = mask,
            protection = protection,
            technical_contact = technical_contact,
            billing_contact = billing_contact,
            security_contact = security_contact
        )
        
        pool.save()


        
    



    class Meta:
        model = CloudDesktop
        fields=['admin_group','shortcode','shared_network','purpose','access_internet','billing_contact','security_contact','mask','protection','technical_contact',
                'base_image_name','initial_image','operating_system',
                'cpu','cpu_cost','memory','memory_cost','storage','storage_cost','gpu','gpu_cost','total','pool_name','auto_logout','pool_maximum',
                'powered_on_desktops','min_desktops','ad_container','ad_groups','additional_details','sla']
        
class ClouddesktopChangeForm(CloudForm):
    title = 'Modify MiDesktop'
    additional_details = forms.CharField(required=False)
    access_internet = forms.ChoiceField(required=False,choices=ACCESS_INTERNET_CHOICES)
    protection = forms.ChoiceField(choices=((True,'Yes'),(False,'No')), widget=forms.Select())  



    class Meta:
        model = CloudDesktop
        fields = ['admin_group','shortcode','account_id','pool_maximum','pool_cost','ad_access_groups','additional_details','access_internet','billing_contact','security_contact','mask','protection','technical_contact']

class ClouddesktopImageChangeForm(CloudForm):
    title = 'Modify Image'
    additional_details = forms.CharField(required=False)
    cpu = forms.ChoiceField(choices=CPU_CHOICES)
    memory = forms.ChoiceField(choices=RAM_CHOICES)
    storage = forms.ChoiceField(choices=STORAGE_CHOICES)
    gpu = forms.ChoiceField(choices=((True,'Yes'),(False,'No')), widget=forms.Select(), initial=False, label="GPU(optional)")
    class Meta:
        model = CloudImage
        fields = ['admin_group','account_id','cpu','cpu_cost','memory','memory_cost','storage','storage_cost','gpu','gpu_cost','total','additional_details']