from django import forms
from django.core import validators
from project.forms.fields import *
from .models import AWS, Azure, GCP, GCPAccount, Container, Network, ImageDisk, Image, Pool
from project.integrations import MCommunity, Openshift
from oscauth.models import LDAPGroup, LDAPGroupMember
from .midesktopchoices import CPU_CHOICES,RAM_CHOICES,STORAGE_CHOICES
from django.forms import ModelForm, formset_factory
from django.core.validators import MinValueValidator

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
    project_name = forms.CharField(help_text='A project is a logical grouping of resources that can be managed together. A project can contain multiple applications, services, and other resources. Projects are used to organize and manage resources in a way that makes sense for your team. The project name must be unique on the hosting cluster. It must be lowercase, contain no special characters, and contain no spaces. Hyphens are permitted.',
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
        os.create_project(self.instaance, self.user.username)

class MiDesktopForm(forms.Form):
    admin_group = forms.ChoiceField(label='MCommunity Admin Group')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user', None)

        super(MiDesktopForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if field != 'sla':
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

        #self.fields['admin_group'].initial = self.instance.owner

    def save(self):
        if 'admin_group' in self.changed_data:
            self.owner = LDAPGroup().lookup( self.cleaned_data.get('admin_group') )

        #super().save()

    def clean(self):
        cleaned_data = super().clean()
        
        for err_field in self.errors:
            self.fields[err_field].widget.attrs['class'] += ' is-invalid'

        return cleaned_data

ACCESS_INTERNET_CHOICES = (('True','Yes, my desktop needs internet access (outside of U of M sites)'),('False','No, my desktop do not need internet access to any network outside of U of M'))
MASK_CHOICES = [["16", "/28 (16 addresses)"], ["32", "/27 (32 addresses)"], ["64", "/26 (64 addresses)"], 
                    ["128", "/25 (128 addresses)"], ["256", "/24 (256 addresses)"]]

CPU_INITIAL = 1.15
MEMORY_INITIAL = 0.96
STORAGE_INITIAL = 5.00
GPU_INITIAL = 0.00
BASE_COST = 31.31
TOTAL_INITIAL = CPU_INITIAL + MEMORY_INITIAL + STORAGE_INITIAL + GPU_INITIAL + BASE_COST

class CalculatorForm(forms.Form):
    cpu = forms.ChoiceField(required=False,choices=CPU_CHOICES)
    cpu_cost = forms.DecimalField(required=False,initial=CPU_INITIAL, widget=forms.TextInput(attrs={'readonly':'true'}))
    memory = forms.ChoiceField(required=False,choices=RAM_CHOICES)
    memory_cost = forms.DecimalField(required=False,initial=MEMORY_INITIAL, widget=forms.TextInput(attrs={'readonly':'true'}))
    storage = forms.ChoiceField(required=False,choices=STORAGE_CHOICES)
    storage_cost = forms.DecimalField(required=False,initial=STORAGE_INITIAL, widget=forms.TextInput(attrs={'readonly':'true'}))
    gpu = forms.ChoiceField(required=False,choices=((True,'Yes'),(False,'No')), widget=forms.Select(), initial=False, label="GPU(optional)")
    gpu_cost = forms.DecimalField(required=False,initial=GPU_INITIAL, widget=forms.TextInput(attrs={'readonly':'true'}))
    total = forms.DecimalField(required=False,initial=TOTAL_INITIAL, widget=forms.TextInput(attrs={'readonly':'true'}))

    template_name = 'services/midesktop-calculator.html'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user', None)

        super(CalculatorForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if hasattr(self.fields[field], 'widget'):
                if not self.fields[field].widget.attrs.get('class',None):
                    self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                print('no widget for', field)

class NetworkForm(forms.Form):
    name = forms.CharField(required=False)
    access_internet = forms.ChoiceField(choices=ACCESS_INTERNET_CHOICES,required=False)
    mask = forms.ChoiceField(choices=MASK_CHOICES,required=False)
    protection = forms.ChoiceField(choices=((True,'Yes'),(False,'No')), widget=forms.Select(), initial=False,required=False)
    technical_contact = forms.CharField(required=False)
    business_contact = forms.CharField(required=False)
    security_contact = forms.CharField(required=False)

    template_name = 'services/network.html'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user', None)

        super(NetworkForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if hasattr(self.fields[field], 'widget'):
                if not self.fields[field].widget.attrs.get('class',None):
                    self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                print('no widget for', field)

class ImageForm(forms.Form):
    name = forms.CharField(required=False)
    initial_image = forms.ChoiceField(required=False, choices=(('Blank','Blank Image'),('Standard','MiDesktop Standard Image')))
    operating_system = forms.ChoiceField(required=False,choices=(('Windows10 64bit','Windows10 64bit'),('Windows11 64bit','Windows11 64bit')))

    template_name = 'services/image.html'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user', None)

        super(ImageForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if hasattr(self.fields[field], 'widget'):
                if not self.fields[field].widget.attrs.get('class',None):
                    self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                print('no widget for', field)


class MiDesktopNewForm(MiDesktopForm):
    title = 'MiDesktop New Order Form'
    shortcode = forms.CharField(validators=[validate_shortcode], required=True)
    pool_type = forms.ChoiceField(label='Pool Type', help_text='Lorem', choices = (("instant_clone","Instant-Clone"),("persistent","Persistent"),("external","External")))
    pool_name = forms.CharField(required=True)
    auto_logout = forms.ChoiceField(required=False,choices=(('Never','Never'),('Immediately','Immediately'),('[Custom]','[Custom]')))
    ad_container = forms.CharField(required=False,)
    ad_groups = forms.CharField(required=False,)
    base_image = forms.IntegerField(required=False)
    pool_quantity = forms.IntegerField(validators=[MinValueValidator(1)])
    pool_total = forms.DecimalField(required=False,initial=None, widget=forms.TextInput(attrs={'readonly':'true'}))
    image_form = ImageForm(prefix="image")
    cpu = forms.ChoiceField(required=False,choices=CPU_CHOICES)
    cpu_cost = forms.DecimalField(required=False,initial=CPU_INITIAL, widget=forms.TextInput(attrs={'readonly':'true'}))
    memory = forms.ChoiceField(required=False,choices=RAM_CHOICES)
    memory_cost = forms.DecimalField(required=False,initial=MEMORY_INITIAL, widget=forms.TextInput(attrs={'readonly':'true'}))
    storage = forms.ChoiceField(required=False,choices=STORAGE_CHOICES)
    storage_cost = forms.DecimalField(required=False,initial=STORAGE_INITIAL, widget=forms.TextInput(attrs={'readonly':'true'}))
    gpu = forms.ChoiceField(required=False,choices=((True,'Yes'),(False,'No')), widget=forms.Select(), initial=False, label="GPU(optional)")
    gpu_cost = forms.DecimalField(required=False,initial=GPU_INITIAL, widget=forms.TextInput(attrs={'readonly':'true'}))
    total = forms.DecimalField(required=False,initial=TOTAL_INITIAL, widget=forms.TextInput(attrs={'readonly':'true'}))
    network_type = forms.ChoiceField(required=False,label='Will you be using a shared network or a dedicated network?',choices = (("private","Shared Network (Private)"),("web-access","Shared Network (Web-Access)"),("dedicated","Dedicated Network")))
    network_form = NetworkForm(prefix="network")
    networks = forms.ChoiceField(label='Dedicated Network', required=False)
    
    sla = forms.BooleanField(required=False)


    class Meta:
        fields=['admin_group',]

    def __init__(self, *args, **kwargs):
        super(MiDesktopNewForm, self).__init__(*args, **kwargs)

        if self.user:
            groups = list(LDAPGroupMember.objects.filter(username=self.user).values_list('ldap_group_id',flat=True))
            network_list = Network.objects.filter(status='A',owner__in=groups).order_by('name')
            choice_list = [(None, '---')]
            for network in network_list:
                choice_list.append((network.name, network.name))
            choice_list.append(('-- New Dedicated Network',"-- New Dedicated Network"))
            choice_list.pop(0)
            self.fields['networks'].choices = choice_list

    def clean(self):
        cleaned_data = super().clean()
        pool_type = cleaned_data.get("pool_type")
        if pool_type == 'instant_clone':
            print('Instant-Clone')
        elif pool_type == 'persistent':
            print('Persistent')
        elif pool_type == 'external':
            print('external')

    def save(self):
        super().save()
        shortcode = self.cleaned_data.get("shortcode")
        name = self.cleaned_data.get("pool_name")
        pool_type = self.cleaned_data.get("pool_type")

        if pool_type == 'external':
            quantity= self.cleaned_data.get("pool_quantity")
            new_pool = Pool(
                        shortcode = shortcode,
                        name = name,
                        quantity = quantity,
                        owner=self.owner,
                        type = pool_type
                    )

            new_pool.save()
            return new_pool
        else:
            base_image_id = int(self.cleaned_data.get("base_image"))
            quantity= self.cleaned_data.get("pool_quantity")
            if base_image_id == 999999999:
                #New Pool with new Image
                image_name=self.data.get("image-name")
                cpu = self.cleaned_data.get("cpu")
                memory = self.cleaned_data.get("memory")
                gpu = self.cleaned_data.get("gpu")
                network_id = self.data.get("network")
                if self.data.get("network") == 'new':
                    new_network = Network(
                        name=self.data['network-name'],
                        size=self.data['network-mask'],
                        owner=self.owner,
                    )

                    new_network.save()

                    new_image = Image(
                        name = image_name,
                        cpu = cpu,
                        memory = memory,
                        gpu = gpu,
                        shared_network = False,
                        network = new_network,
                        owner=self.owner
                    )

                    new_image.save()

                    new_pool = Pool(
                        shortcode = shortcode,
                        name = name,
                        quantity = quantity,
                        owner=self.owner,
                        type = pool_type
                    )

                    new_pool.save()

                    new_pool.images.add(new_image)
                    return new_pool

                elif self.cleaned_data.get('network_type') != 'dedicated':
                    new_image = Image(
                        name = image_name,
                        cpu = cpu,
                        memory = memory,
                        gpu = gpu,
                        shared_network = True,
                        network = None,
                        owner=self.owner
                    )
                    new_image.save()

                    new_pool = Pool(
                        shortcode = shortcode,
                        name = name,
                        quantity = quantity,
                        owner=self.owner,
                        type = pool_type
                    )

                    new_pool.save()

                    new_pool.images.add(new_image)
                    return new_pool
                
                else:
                    new_image = Image(
                        name = image_name,
                        cpu = cpu,
                        memory = memory,
                        gpu = gpu,
                        shared_network = False,
                        network = Network.objects.get(pk = network_id),
                        owner=self.owner
                    )

                    new_image.save()

                    new_pool = Pool(
                        shortcode = shortcode,
                        name = name,
                        quantity = quantity,
                        owner=self.owner,
                        type = pool_type
                    )

                    new_pool.save()

                    new_pool.images.add(new_image)
                    return new_pool
                
            else:
                base_image_object = Image.objects.get(id = base_image_id)
                new_pool = Pool(
                    shortcode = shortcode,
                    name = name,
                    quantity = quantity,
                    owner=self.owner,
                    type = pool_type
                )
                new_pool.save()

                new_pool.images.add(base_image_object)
                return new_pool


class DiskForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField()
    name.widget.attrs.update({'class': 'form-control col-2', 'readonly': True})  

    size = forms.IntegerField(initial=10)
    size.widget.attrs.update({'class': 'form-control disk-size validate-integer', 'step': 10, 'min': '10'})  

    class Meta:
        model = ImageDisk
        fields = ['id', 'name', 'size']

class MiDesktopNewImageForm(MiDesktopForm):
    name = forms.CharField()
    initial_image = forms.ChoiceField(choices=(('Blank','Blank Image'),('Standard','MiDesktop Standard Image')))
    operating_system = forms.ChoiceField(choices=(('Windows10 64bit','Windows10 64bit'),('Windows 11 64bit','Windows 11 64bit')))

    calculator_form = CalculatorForm(prefix="calculator")
    network_type = forms.ChoiceField(label='Will you be using a shared network or a dedicated network?', choices = (("private","Shared Network (Private)"),("web-access","Shared Network (Web-Access)"),("dedicated","Dedicated Network")))

    network_name = forms.CharField(required=False)
    access_internet = forms.ChoiceField(choices=ACCESS_INTERNET_CHOICES,required=False)
    mask = forms.ChoiceField(choices=MASK_CHOICES,required=False)
    protection = forms.ChoiceField(choices=((True,'Yes'),(False,'No')), widget=forms.Select(), initial=False,required=False)
    technical_contact = forms.CharField(required=False)
    business_contact = forms.CharField(required=False)
    security_contact = forms.CharField(required=False)
    
    networks = forms.ChoiceField(label='Dedicated Network', required=False)
    title = 'MiDesktop New Image Order Form'

    
    
    class Meta:
        fields=['admin_group']

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        image_name = self.data['name']

        cpu = self.data['calculator-cpu']
        memory = self.data['calculator-memory']
        gpu = self.data['calculator-gpu']
        
        network_type = self.data['network_type']
        network_name = self.data['network_name']

        super().save()

        if(network_type == 'dedicated' and len(network_name) == 0):
            #'New Image on Network thats already created'
            network_id = int(self.data['network'])

            new_image = Image(
                name = image_name,
                cpu = cpu,
                memory = memory,
                gpu = gpu,
                shared_network = False,
                network = Network.objects.get(pk = network_id),
                owner=self.owner
            )
            new_image.save()
            return new_image

        elif(network_type == 'dedicated' and len(network_name) > 0):
            #New Image on New Network'
            new_network = Network(
                name=self.data['network_name'],
                size=self.data['mask'],
                owner=self.owner,
            )
            new_network.save()

            new_image = Image(
                    name = image_name,
                    cpu = cpu,
                    memory = memory,
                    gpu = gpu,
                    shared_network = False,
                    network = new_network,
                    owner=self.owner
                )
            new_image.save()
            
            return new_image

        else:
            #New Image on Shared Network'
            new_image = Image(
                    name = image_name,
                    cpu = cpu,
                    memory = memory,
                    gpu = gpu,
                    shared_network = True,
                    network = None,
                    owner=self.owner
                )
            new_image.save()
            
            return new_image

class MiDesktopChangeImageForm(forms.ModelForm):
    name = forms.CharField(required=False)
    calculator_form = CalculatorForm(prefix="calculator")
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self):
        self.network = self.instance.network
        self.shared_network = self.instance.shared_network

        super().save()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user', None)

        super(MiDesktopChangeImageForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if hasattr(self.fields[field], 'widget'):
                if not self.fields[field].widget.attrs.get('class',None):
                    self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                print('no widget for', field)
    class Meta:
        model = Image
        exclude=['admin_group','network','owner','status']


class MiDesktopNewNetworkForm(MiDesktopForm):
    title = 'MiDesktop New Network Order Form'
    name = forms.CharField()
    access_internet = forms.ChoiceField(choices=ACCESS_INTERNET_CHOICES)
    mask = forms.ChoiceField(choices=MASK_CHOICES)
    protection = forms.ChoiceField(choices=((True,'Yes'),(False,'No')), widget=forms.Select(), initial=False)
    technical_contact = forms.CharField()
    business_contact = forms.CharField()
    security_contact = forms.CharField()
    
    class Meta:
        fields = ['admin_group']

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data

    def save(self, commit=True):
        super().save()
        new_network = Network(
            name=self.data['name'],
            size=self.data['mask'],
            owner=self.owner,
        )
        if commit:
            new_network.save()
        return new_network
    
class MiDesktopChangeNetworkForm(forms.ModelForm):
    name = forms.CharField()
    size = forms.ChoiceField(choices=MASK_CHOICES)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user', None)

        super(MiDesktopChangeNetworkForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if hasattr(self.fields[field], 'widget'):
                if not self.fields[field].widget.attrs.get('class',None):
                    self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                print('no widget for', field)

    class Meta:
        model = Network
        fields = ['name','size']


class InstantClonePoolChangeForm(forms.ModelForm):
    shortcode = forms.CharField(validators=[validate_shortcode], required=True)
    name = forms.CharField(required=True)
    images = forms.ChoiceField(label='Image', required=True)
    quantity = forms.IntegerField(validators=[MinValueValidator(1)])
    total = forms.DecimalField(required=False,initial=None, widget=forms.TextInput(attrs={'readonly':'true'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        self.image = kwargs.pop('image', None)
        self.total = round(self.image.total_cost,2)
        kwargs.pop('user', None)

        super(InstantClonePoolChangeForm, self).__init__(*args, **kwargs)
        if self.user:

            image_list = Image.objects.filter(status='A',owner__in=[self.instance.owner.id]).order_by('name')
            choice_list = [(None, '---')]
            for image in image_list:
                choice_list.append((image.name, image.name))
            self.fields['images'].choices = choice_list

        for field in self.fields:
            if hasattr(self.fields[field], 'widget'):
                if not self.fields[field].widget.attrs.get('class',None):
                    self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                print('no widget for', field)
        self.fields['total'].initial = self.total
        self.fields['images'].initial = self.image.name
        

    class Meta:
        model = Pool
        fields = ['shortcode','name','quantity']

class PersistentPoolChangeForm(forms.ModelForm):
    shortcode = forms.CharField(validators=[validate_shortcode], required=True)
    name = forms.CharField(required=True)
    multi_image = forms.CharField(required=False)
    total = forms.DecimalField(required=False,initial=None, widget=forms.TextInput(attrs={'readonly':'true'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        #self.total = round(self.image.total_cost,2)
        kwargs.pop('user', None)

        super(PersistentPoolChangeForm, self).__init__(*args, **kwargs)
        if self.user:
            image_list = Image.objects.filter(status='A',owner__in=[self.instance.owner.id]).order_by('name')
            choice_list = [(None, '---')]
            for image in image_list:
                choice_list.append((image.name, image.name))
            #self.fields['images'].choices = choice_list

        for field in self.fields:
            if hasattr(self.fields[field], 'widget'):
                if not self.fields[field].widget.attrs.get('class',None):
                    self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                print('no widget for', field)
        #self.fields['total'].initial = self.total

    def save(self):
        data = self.cleaned_data
        self.instance.images.clear()
        multi_image = data['multi_image']
        images = [int(x) for x in multi_image.split(',')]
        for image_id in images:
            image = Image.objects.get(id = image_id)
            self.instance.images.add(image)
        
        super().save()
            

    class Meta:
        model = Pool
        fields = ['shortcode','name']


class ExternalPoolChangeForm(forms.ModelForm):
    shortcode = forms.CharField(validators=[validate_shortcode], required=True)
    name = forms.CharField(required=True)
    quantity = forms.IntegerField(validators=[MinValueValidator(1)])
    total = forms.DecimalField(required=False,initial=None, widget=forms.TextInput(attrs={'readonly':'true'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user', None)

        super(ExternalPoolChangeForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if hasattr(self.fields[field], 'widget'):
                if not self.fields[field].widget.attrs.get('class',None):
                    self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                print('no widget for', field)

    class Meta:
        model = Pool
        fields = ['shortcode','name','quantity']