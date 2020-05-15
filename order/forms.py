from django import forms
from django.forms import ModelForm
#from .models import Product, Service, Action, Feature, FeatureCategory, FeatureType, Restriction, ProductCategory, Element, StorageInstance, Step, StorageMember, StorageHost, StorageRate
from .models import *
from pages.models import Page
from project.pinnmodels import UmOSCBuildingV

from project.forms.fields import *

def get_storage_options(type):
    opt_list = []
    for opt in StorageRate.objects.filter(type=type):
        label = f'{opt.label} ({opt.rate} / per GB)'
        opt_list.append((opt.id, label))

    return opt_list

class TabForm(forms.Form):

    template = 'order/base_form.html'

    def get_next_tab(self, action_id):

        step = Step.objects.get(name='detailsNFS')
        next_tab = TabForm(step)
        return next_tab

    def clean(self):
        
        for field in self.fields:
            if self.has_error(field):
                if self.fields[field].type == 'Radio' or self.fields[field].type == 'Checkbox':
                    self.fields[field].widget.attrs.update({'class': ' is-invalid'}) #form-control makes radio buttons wonky
                else:
                    self.fields[field].widget.attrs.update({'class': ' is-invalid form-control'}) 

    def get_summary(self, visible):

        summary = []

        for key, value in self.cleaned_data.items():
            field = self.fields[key]


            if key in visible:  # Add visible fields to the review page
                label = field.label

                if field.type == 'Radio':
                    for choice in field.choices:
                        if str(choice[0]) == value:
                            value = choice[1]

                if field.type == 'Checkbox':  
                    label = field.choices[0][1]
                    if len(value) > 0:  #TODO handle more than one Yes/No field.
                        value = 'Yes'
                    else:
                        value = 'No'

                
                summary.append({'label': label, 'value': value})

        return summary

    #def is_valid(self):
    #    valid = super(TabForm, self).is_valid()
    #    return valid

    def __init__(self, tab, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TabForm, self).__init__(*args, **kwargs)
    #def __init__(self, tab, *args, **kwargs):
    #    super(TabForm, self, *args, **kwargs).__init__()

        self.tab_name = tab.name
        element_list = Element.objects.all().filter(step_id = tab.id).order_by('display_seq_no')

        for element in element_list:  # Bind fields based on setup data in Admin Module

            if element.type == 'Radio':
                #field = forms.ChoiceField(choices=eval(element.attributes), widget=forms.RadioSelect(attrs={'class': 'form-control'}))
                field = forms.ChoiceField(choices=eval(element.attributes), widget=forms.RadioSelect())
                field.template_name = 'project/radio.html'
            elif element.type == 'Chart':
                field = forms.ChoiceField(label=element.label, help_text=element.description
                                        , widget=forms.Select(attrs={'class': "form-control"}), choices=Chartcom.get_user_chartcoms(request.user.id))
                                                                        #AuthUserDept.get_order_departments(request.user.id)
                field.dept_list = Chartcom.get_user_chartcom_depts(request.user.id) #['12','34','56']
            elif element.type == 'NU':
                field = forms.IntegerField(widget=forms.NumberInput(attrs={'min': "1", 'class': 'form-control'}))
                field.template_name = 'project/number.html'
            elif element.type == 'ST':
                field = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
                field.template_name = 'project/text.html'
            elif element.type == 'Checkbox':
                field = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), choices=eval(element.attributes))
                field.template_name = 'project/checkbox.html'
            elif element.type == 'HTML':
                field = forms.CharField(required=False)
                field.template_name = 'project/static.html'
            elif element.type == 'McGroup--':
                field = McGroup()
                field.template_name = 'project/static.html'
            else:
                # Use custom field from project.forms.fields
                field = globals()[element.type](label=element.name)
                #field.field_name = element.name
                field.template_name = 'project/text.html'
                #field = forms.IntegerField(label=element.label, help_text=element.description)

            field.name = element.name
            #field.current_user = self.request.user
            field.label = element.label
            field.help_text = element.help_text
            field.description = element.description
            field.attributes = element.attributes
            field.display_seq_no = element.display_seq_no
            field.display_condition = element.display_condition
            field.type = element.type

            self.fields.update({element.name: field})
        

class BillingForm(TabForm):

    template = 'order/billing.html'

    def get_summary(self, visible):

        summary = []
        occ = self.data.get('cc_oneTimeCharges')
        if occ:
            summary.append({'label': 'One Time Charges', 'value': occ})

        mrc = self.data.get('cc_MRC')
        if mrc:
            summary.append({'label': 'Monthly Recurring Charges', 'value': mrc})

        loc = self.data.get('cc_LOC')
        if loc:
            summary.append({'label': 'Local Charges', 'value': loc})

        ld = self.data.get('cc_LD')
        if ld:
            summary.append({'label': 'Long Distance Charges', 'value': ld})

        return summary



    def __init__(self, *args, **kwargs):
        super(BillingForm, self).__init__(*args, **kwargs)

        action_id = self.request.POST['action_id']
        self.charge_types = ChargeType.objects.filter(action__id=action_id).order_by('display_seq_no')
        self.dept_list = Chartcom.get_user_chartcom_depts(self.request.user.id) 
        self.chartcom_list = UserChartcomV.objects.filter(user=self.request.user).order_by('name')


class FeaturesForm(TabForm):

    features = forms.ModelMultipleChoiceField(
        queryset=Feature.objects.all(), 
        widget=forms.CheckboxSelectMultiple(),
    )
    
    categories = FeatureCategory.objects.all()
    types = FeatureType.objects.all()
    features = Feature.objects.all().order_by('display_seq_no')

    for cat in categories:
        cat.types = []
        for type in types:
            q = features.filter(type=type).filter(category=cat).order_by('display_seq_no')
            if q:
                cat.types.append(q)
                cat.types[-1].label = type.label
                cat.types[-1].description = type.description

    template = 'order/features.html'

    class Meta:
        model = Feature
        fields = ('name', 'description',) 


class RestrictionsForm(TabForm):
    res = Restriction.objects.all()
    list = FeatureCategory.objects.all()

    for cat in list:
        cat.res = res.filter(category=cat).order_by('display_seq_no')
        last = cat.res.count()
        cat.last = cat.res[last-1].id

    information = Page.objects.get(permalink='/restriction')

    template = 'order/restrictions.html'


class AddlInfoForm(TabForm):

    def is_valid(self, *args, **kwargs):
        super(AddlInfoForm, self).is_valid(*args, **kwargs)
        return True

    #TRUE_FALSE_CHOICES = (
    #(True, 'Yes'),
    #(False, 'No')
    #)

    #contact_yn = forms.ChoiceField(choices = TRUE_FALSE_CHOICES, label="Are you the on site contact?", required=True)
    #contact_yn.type = 'Radio'

    #contact_id = forms.CharField(label='Uniqname of the on site contact person', max_length=8)
    #contact_id.type = 'ST'

    #contact_name = forms.CharField(label='Name of the on site contact person', max_length=40)
    #contact_name.type = 'ST'

    #contact_number = forms.CharField(label='Best number to contact', max_length=10)
    #comments = forms.CharField(label='Comments', required=False, widget=forms.Textarea(attrs={'cols':'100', 'class':'form-control'}) )
    file = forms.FileField(label="Please attach any drawings, spreadsheets or floor plans with jack locations as needed", required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
    file.type = 'file'
    template = 'order/addl_info.html'


class VolumeSelectionForm(TabForm):
    template = 'order/volume_selection.html'

    total_cost = 0

    def get_summary(self, *args, **kwargs):
        #summary = super().get_summary(*args, **kwargs)

        instance = StorageInstance.objects.get(id=self.data['instance_id'])

        if self.data.get('volaction') == 'Delete':
            summary = [{'label': 'Are you sure you want to delete this volume?', 'value': ''}
                        ,{'label': 'Volume Name:', 'value': instance.name}
                        ,{'label': 'Owner:', 'value': instance.owner.name}]
        else:
            summary = [{'label': 'Volume Name:', 'value': instance.name}]

        return summary


    def is_valid(self, *args, **kwargs):
        super(VolumeSelectionForm, self).is_valid(*args, **kwargs)
        return True

    def __init__(self, *args, **kwargs):
        super(VolumeSelectionForm, self).__init__(*args, **kwargs)

        if not self.is_bound:
            groups = list(StorageMember.objects.filter(username=self.request.user).values_list('storage_owner_id'))
            if self.request.path == '/orders/wf/47':
                #self.volume_list = StorageMember.objects.filter(username=self.request.user, storage_instance__type='NFS').distinct('storage_instance__name').order_by('storage_instance__name')
                self.volume_list = StorageInstance.objects.filter(type='NFS',owner__in=groups).order_by('name')

            elif self.request.path == '/orders/wf/49':
                #self.volume_list = StorageMember.objects.filter(username=self.request.user, storage_instance__type='CIFS').distinct('storage_instance__name').order_by('storage_instance__name')
                self.volume_list = StorageInstance.objects.filter(type='CIFS',owner__in=groups).order_by('name')
            else:
                #self.volume_list = StorageMember.objects.filter(username=self.request.user).distinct('storage_instance__name').order_by('storage_instance__name')
                self.volume_list = StorageInstance.objects.filter(owner__in=groups).order_by('name')
                
                for vol in self.volume_list:
                    self.total_cost = self.total_cost + vol.total_cost
                    
                self.template = 'order/volume_review.html'


class AccessNFSForm(TabForm):
    template = 'order/nfs_access.html'

    #def clean_volumeAdmin(self):
    #    if self.data['volumeAdmin'] == '0':
    #        raise forms.ValidationError('Root access is not allowed.  Enter a value other than 0', code='root')


    def get_summary(self, *args, **kwargs):
        summary = super().get_summary(*args, **kwargs)

        hosts = self.data.getlist('permittedHosts')

        if len(hosts) > 1:
            host_value = ''
            for host in hosts:
                if host_value:
                    host_value = host_value + ',' + host
                else:
                    host_value = host

            summary[2]['value'] = host_value

        instance_id = self.data.get('instance_id')
        if instance_id:

            si = StorageInstance.objects.get(id=instance_id)
            if summary[0]['value'] != si.uid:
                summary[0]['label'] = '*' + summary[0]['label']
            if summary[1]['value'] != si.owner:
                summary[1]['label'] = '*' + summary[1]['label']
        
            host_list = list(StorageHost.objects.filter(storage_instance=si).values('name').values_list('name', flat=True))
            host_list.insert(0,'')
            if hosts != host_list:
                if len(summary) > 2:
                    summary[2]['label'] = '*' + summary[2]['label']


        return summary

    def __init__(self, *args, **kwargs):
        super(AccessNFSForm, self).__init__(*args, **kwargs)
        self['permittedHosts'].field.required = False

        if self.request:
            if self.request.method == 'POST':
                instance_id = self.request.POST.get('instance_id')
                if instance_id:
                    si = StorageInstance.objects.get(id=instance_id)
                    self.fields["volumeAdmin"].initial = si.uid
                    self.fields["owner"].initial = si.owner
                    self.host_list = StorageHost.objects.filter(storage_instance_id=instance_id)
        else:
            self.host_list = []
            hosts = self.data.getlist('permittedHosts')
            for host in hosts:
                if host:
                    self.host_list.append({'name': host})


class DetailsNFSForm(TabForm):

    def get_summary(self, *args, **kwargs):
        summary = super().get_summary(*args, **kwargs)
        instance_id = self.data.get('instance_id')
        
        if instance_id:
            si = StorageInstance.objects.get(id=instance_id)
            if summary[0]['value'] != si.name:
                summary[0]['label'] = '*' + summary[0]['label']
            if self.data.get('selectOptionType') != str(si.rate_id):
                summary[1]['label'] = '*' + summary[1]['label']
            if summary[2]['value'] != si.size:
                summary[2]['label'] = '*' + summary[2]['label']
            if si.flux:
                if summary[3]['value'] == 'No':
                    summary[3]['label'] = '*' + summary[3]['label']
            else:
                if summary[3]['value'] == 'Yes':
                    summary[3]['label'] = '*' + summary[3]['label']

        return summary

    def __init__(self, *args, **kwargs):
        super(DetailsNFSForm, self).__init__(*args, **kwargs)
        self['flux'].field.required = False

        if self.request:
            if self.request.method == 'POST':
                instance_id = self.request.POST.get('instance_id')
                if instance_id:
                    si = StorageInstance.objects.get(id=instance_id)
                    self.fields["sizeGigabyte"].initial = si.size
                    self.fields["storageID"].initial = si.name
                    self.fields["selectOptionType"].initial = si.rate_id
                    self.fields['flux'].initial = si.flux  

class DetailsCIFSForm(TabForm):

    def get_summary(self, *args, **kwargs):
        summary = super().get_summary(*args, **kwargs)
        instance_id = self.data.get('instance_id')
        
        if instance_id:
            si = StorageInstance.objects.get(id=instance_id)
            if summary[0]['value'] != si.owner:
                summary[0]['label'] = '*' + summary[0]['label']
            if summary[1]['value'] != si.ad_group:
                summary[1]['label'] = '*' + summary[1]['label']
            if summary[2]['value'] != si.name:
                summary[2]['label'] = '*' + summary[2]['label']
            if self.data['selectOptionType'] != str(si.rate_id):
                summary[3]['label'] = '*' + summary[3]['label']
            if summary[4]['value'] != si.size:
                summary[4]['label'] = '*' + summary[4]['label']

        return summary

    def __init__(self, *args, **kwargs):
        super(DetailsCIFSForm, self).__init__(*args, **kwargs)

        if self.request:
            if self.request.method == 'POST':
                instance_id = self.request.POST.get('instance_id')
                if instance_id:
                    si = StorageInstance.objects.get(id=instance_id)
                    self.fields["mcommGroup"].initial = si.owner
                    self.fields["activeDir"].initial = si.ad_group
                    self.fields["netShare"].initial = si.name
                    self.fields["selectOptionType"].initial = si.rate_id
                    self.fields["sizeGigabyte"].initial = si.size


class BackupDetailsForm(TabForm):
    template = 'order/backup_details.html'


    def is_valid(self, *args, **kwargs):
        super(BackupDetailsForm, self).is_valid(*args, **kwargs)
        return True

class BillingStorageForm(TabForm):

    def __init__(self, *args, **kwargs):
        super(BillingStorageForm, self).__init__(*args, **kwargs)
        total_cost = 0

        if self.request:
            if self.request.method == 'POST':
                instance_id = self.request.POST.get('instance_id')
                #option = StorageRate.objects.get(id=self.request.POST['selectOptionType'])
                #total_cost = option.get_total_cost(self.request.POST['sizeGigabyte'])

                if instance_id:
                    si = StorageInstance.objects.get(id=instance_id)
                    self.fields["shortcode"].initial = si.shortcode
                    self.fields["billingAuthority"].initial = 'yes'
                    self.fields["serviceLvlAgreement"].initial = 'yes'
        #else:
            #option = StorageRate.objects.get(id=self.data['selectOptionType'])
            #total_cost = option.get_total_cost(self.data['sizeGigabyte'])

        descr = self.fields['totalCost'].description.replace('~', str(total_cost))
        self.fields['totalCost'].description = descr

    def get_summary(self, *args, **kwargs):
        summary = super().get_summary(*args, **kwargs)
        #option = StorageRate.objects.get(id=self.data['selectOptionType'])
        #total_cost = option.get_total_cost(self.data['sizeGigabyte'])
        total_cost = '33.33'
        summary.append({'label': 'Total Cost', 'value': str(total_cost)})

        instance_id = self.data.get('instance_id')
        
        if instance_id:
            si = StorageInstance.objects.get(id=instance_id)
            if self.data['shortcode'] != si.shortcode:
                summary[0]['label'] = '*' + summary[0]['label']


        return summary


class VoicemailForm(TabForm):
    template = 'order/voicemail.html'


class ContactCenterForm(TabForm):
    phone_number = forms.CharField(label='summary', max_length=12)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols':'100'}) )

    template = 'order/contact_center.html'


class ReviewForm(TabForm):

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)

        if self.request.POST.get('action_id') == '47' or self.request.POST.get('action_id') == '49':
            item_id = self.request.POST.get('item_id')
            instance_id = self.request.POST.get('instance_id')

    #summary = forms.CharField(label='summary', max_length=6)
    template = 'order/review.html'


class AuthCodeCancelForm(TabForm):
    TYPE_CHOICES = (
    ('Cancel', 'Cancel'),
    ('Change', 'Change')
    )
    action = forms.ChoiceField(choices = TYPE_CHOICES, required=True)
    subscriber_id = forms.CharField(label='summary', max_length=100)
    name = forms.CharField(label='name', max_length=100)
    template = 'order/auth_code_cancel.html'


class AuthCodeForm(TabForm):
    TYPE_CHOICES = (
    ('Individual', 'Individual'),
    ('Workgroup', 'Workgroup')
    )
    type = forms.ChoiceField(choices = TYPE_CHOICES, required=True)
    name = forms.CharField(label='summary', max_length=100)
    template = 'order/auth_code.html'


class CMCCodeForm(TabForm):
    code = forms.CharField(label='CMC Code', max_length=100)
    template = 'order/cmc_code.html'


class NewLocationForm(TabForm):
    building_list = UmOSCBuildingV.objects.all()
    new_building_code = forms.CharField(label='Building Code', max_length=100)
    new_building_name = forms.CharField(label='Building Name', max_length=100)
    new_floor = forms.CharField(label='Floor', max_length=100)
    new_room = forms.CharField(label='Room', max_length=100)

    template = 'order/location.html'


class EquipmentForm(TabForm):
    cat = ['Basic','VOIP']
    cat[0] = Product.objects.all().filter(category=1).order_by('display_seq_no')
    cat[0].id = 'basic'
    cat[1] = Product.objects.all().filter(category__in=[2, 4]).order_by('display_seq_no') # Voip and Conference
    cat[1].id = 'voip'
    template = 'order/equipment.html'


class ProductForm(TabForm):
    category_list = ProductCategory.objects.all().order_by('display_seq_no') 
    product_list = Product.objects.all().order_by('category','display_seq_no') 
    template = 'order/products.html'


class PhoneLocationForm(TabForm):
    phone_number = forms.CharField(label='Current Phone Number')
    building = forms.CharField(label='Building', max_length=100)
    floor = forms.CharField(label='Floor', max_length=100)
    room = forms.CharField(label='Room', max_length=100)
    jack = forms.CharField(max_length=100)
    template = 'order/phone_location.html'
