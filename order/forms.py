from django import forms
from django.forms import ModelForm
#from .models import Product, Service, Action, Feature, FeatureCategory, FeatureType, Restriction, ProductCategory, Element, StorageInstance, Step, StorageMember, StorageHost, StorageRate
from .models import *
from pages.models import Page
from project.pinnmodels import UmOSCBuildingV
from oscauth.models import LDAPGroupMember

from project.forms.fields import *

def get_storage_options(action):
    opt_list = []
    for opt in StorageRate.objects.filter(type=action.override['storage_type'], service=action.service):
        label = f'{opt.label} ({opt.rate} / per {opt.unit_of_measure})'
        opt_list.append((opt.id, label))

    return opt_list

class TabForm(forms.Form):

    template = 'order/base_form.html'

    def set_initial(self, instance_id):
        vol = self.vol.objects.get(id=instance_id)
        self.instance = vol

        for fieldname, field in self.fields.items():
            if hasattr(vol, fieldname):
                field.initial = getattr(vol,fieldname)
            elif type(field) == forms.MultipleChoiceField:
                field.initial = vol.get_checkboxes()
            elif fieldname == 'selectOptionType':
                field.initial = vol.rate_id
            
            if fieldname == 'sensitive_regulated':
                if vol.sensitive_regulated:
                    field.initial = 'yessen'
                else:
                    field.initial = 'nosen'


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

                if self.action.type == 'M':
                    if key in self.changed_data:
                        label = '*' + label

                if field.type == 'Radio':
                    for choice in field.choices:
                        if str(choice[0]) == value:
                            value = choice[1]

                if field.type == 'Checkbox':  
                    label = field.choices[0][1]
                    if len(field.choices) > 1:  # Process list of options
                        label = field.label
                        value = ', '.join(value)
                    elif len(value) > 0:  
                        value = 'Yes'
                    else:
                        value = 'No'

                if field.type == 'List':  
                    list = self.data.getlist(key)
                    value = ', '.join(list)

                summary.append({'label': label, 'value': value})

        return summary

    def __init__(self, tab, action, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TabForm, self).__init__(*args, **kwargs)

        if action.service.id == 7:
            self.vol = StorageInstance
            self.host = StorageHost
        elif action.service.id == 8:
            self.vol = BackupDomain
        else:
            self.vol = ArcInstance
            self.host = ArcHost

        self.action = action

        self.tab_name = tab.name

        exclude_list = self.action.get_hidden_fields()
        element_list = Element.objects.filter(step_id = tab.id).exclude(name__in=exclude_list).order_by('display_seq_no')

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
                field.initial = element.attributes
                field.template_name = 'project/number.html'
            elif element.type == 'ST' or element.type == 'List':
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
            field.target = element.target

            # Check for action specific overrides
            if 'elements' in action.override:
                if field.name in action.override['elements']:
                    override = action.override['elements'][field.name]
                    for key in override:
                        setattr(field, key, override[key])



            self.fields.update({element.name: field})
        
        if self.request:  # If modifying existing data, prepoulate the form
            if self.request.method == 'POST':
                instance_id = self.request.POST.get('instance_id')
                if instance_id:
                    self.set_initial(instance_id)


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

    file = forms.FileField(label="Please attach any drawings, spreadsheets or floor plans with jack locations as needed", required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
    file.type = 'file'
    template = 'order/addl_info.html'


    def is_valid(self, *args, **kwargs):
        super(AddlInfoForm, self).is_valid(*args, **kwargs)
        return True


class SubscriptionSelForm(TabForm):
    template = 'order/subscription_review.html'

    def get_summary(self, *args, **kwargs):
        #summary = super().get_summary(*args, **kwargs)

        subscription = BackupDomain.objects.get(id=self.data['instance_id'])

        if self.data.get('volaction') == 'Delete':
            summary = [{'label': 'Are you sure you want to delete this subscription?', 'value': ''}
                        ,{'label': 'Domain Name:', 'value': subscription.name}
                        ,{'label': 'Owner:', 'value': subscription.owner.name}]
        else:
            summary = [{'label': 'Domain Name:', 'value': subscription.name}]

        return summary

    def is_valid(self, *args, **kwargs):
        super(SubscriptionSelForm, self).is_valid(*args, **kwargs)
        return True

    def __init__(self, *args, **kwargs):
        super(SubscriptionSelForm, self).__init__(*args, **kwargs)

        self.subscription_list = BackupDomain().get_user_subscriptions(self.request.user.username)
        self.total_cost = 0

        for sub in self.subscription_list:
            sub.node_list = BackupNode.objects.filter(backup_domain=sub)
            sub.node_count = sub.node_list.count()
            self.total_cost = self.total_cost + sub.total_cost
        
        self.total_cost = round(self.total_cost,2)

        if not self.is_bound:
            action_id = int(self.request.path[11:])

            if action_id == 62:
                self.template = 'order/subscription_selection.html'


class VolumeSelectionForm(TabForm):
    template = 'order/volume_selection.html'

    total_cost = 0

    def get_summary(self, *args, **kwargs):
        #summary = super().get_summary(*args, **kwargs)

        instance = self.vol.objects.get(id=self.data['instance_id'])

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
            groups = list(LDAPGroupMember.objects.filter(username=self.request.user).values_list('ldap_group_id'))
            action_id = int(self.request.path[11:])
            action = Action.objects.get(id=action_id)
            service = action.service

            if 'storage_type' in action.override:
                vol_type = action.override['storage_type']
                self.volume_list = self.vol.objects.filter(service=service, type=vol_type, owner__in=groups).order_by('name')
            else:
                self.volume_list = self.vol.objects.filter(service=service, owner__in=groups).order_by('name')

                for volume in self.volume_list:
                    self.total_cost = self.total_cost + volume.total_cost
                    
                self.template = 'order/volume_review.html'


class AccessNFSForm(TabForm):
    template = 'order/nfs_access.html'

    def get_summary(self, *args, **kwargs):
        summary = super().get_summary(*args, **kwargs)

        #hosts = self.data.getlist('permittedHosts')

        #if len(hosts) > 1:
        #    host_value = ''
        #    for host in hosts:
        #        if host_value:
        #            host_value = host_value + ',' + host
        #        else:
        #            host_value = host

        #    summary[2]['value'] = host_value

        return summary

    def __init__(self, *args, **kwargs):
        super(AccessNFSForm, self).__init__(*args, **kwargs)
        self['permittedHosts'].field.required = False

        if self.request.method == 'POST': # Skip for initial load on Add
            if self.is_bound:   # Reload Host g
                self.host_list = []
                hosts = self.data.getlist('permittedHosts')
                for host in hosts:
                    if host:
                        self.host_list.append({'name': host})


            else:  # Load instance data if it exists.
                self.host_list = self.instance.get_hosts()

                #if self.
            #    instance_id = self.request.POST.get('instance_id')
            #    if instance_id: # 
            #        si = self.vol.objects.get(id=instance_id)
            #        self.fields["volumeAdmin"].initial = si.uid
            #        self.fields["owner"].initial = si.owner
            #        self.host_list = StorageHost.objects.filter(storage_instance_id=instance_id)



class DetailsNFSForm(TabForm):

    def set_initial(self, instance_id, *args, **kwargs):
        super().set_initial(instance_id, *args, **kwargs)

        if 'multi_protocol' in self.fields:
            if self.instance.multi_protocol:
                self.fields['multi_protocol'].initial = 'ycifs'
            else:
                self.fields['multi_protocol'].initial = 'ncifs'

        #TODO Set checkboxes
        #self.fields['hipaaOptions'].initial == ['armis','globus_phi']

    def __init__(self, *args, **kwargs):
        super(DetailsNFSForm, self).__init__(*args, **kwargs)
        if 'flux' in self:
            self['flux'].field.required = False

        if 'hipaaOptions' in self.fields:
            if self.request.POST['sensitive_regulated'] == 'nosen': 
                self['nonHipaaOptions'].field.required = False
                self.fields.pop('hipaaOptions')

            if self.request.POST['sensitive_regulated'] == 'yessen': 
                self['hipaaOptions'].field.required = False
                self.fields.pop('nonHipaaOptions')

            #print(self.data, self.request.POST) 

        #if self.request:
        #    if self.request.method == 'POST':
        #        instance_id = self.request.POST.get('instance_id')
        #        if instance_id:
        #            si = self.vol.objects.get(id=instance_id)
        #            self.fields["sizeGigabyte"].initial = si.size
        #            self.fields["storageID"].initial = si.name
        #            self.fields["selectOptionType"].initial = si.rate_id
        #            self.fields['flux'].initial = si.flux  

class DetailsCIFSForm(TabForm):
    pass


class BackupDetailsForm(TabForm):
    template = 'order/backup_details.html'

    def __init__(self, *args, **kwargs):
        super(BackupDetailsForm, self).__init__(*args, **kwargs)

        self.time_list = eval(self.fields['backupTime'].attributes)

        if self.request.method == 'POST': # Skip for initial load on Add
            if self.is_bound:   # Reload Host list
                self.node_list = []
                nodes = self.data.getlist('nodeNames')
                times = self.data.getlist('backupTime')


                for count, node in enumerate(nodes):
                    if node:
                        self.node_list.append({'name': node, 'time': times[count]})
            else:
                instance_id = self.request.POST.get('instance_id')
                if instance_id: 
                    bd = BackupDomain.objects.get(id=instance_id)
                    self.fields["mCommunityName"].initial = bd.owner
                    self.node_list = BackupNode.objects.filter(backup_domain=instance_id)
        else:
            self.node_list = []
            self.node_list.append({'name': '', 'time': ''})

    def get_summary(self, *args, **kwargs):
        summary = super().get_summary(*args, **kwargs)
        nodes = self.data.getlist('nodeNames')
        times = self.data.getlist('backupTime')
        if len(nodes) > 1:
            node_value = ''
            times[0] = ''
            for count, node in enumerate(nodes):

                if node_value:
                    node_value = node_value + ', ' + node + '@' + times[count]
                else:
                    if node:
                        node_value = node + '@' + times[count]

            summary[1]['value'] = node_value
            summary.pop(2) # Remove backupTime field from summary
            
        return summary

class BillingStorageForm(TabForm):

    def __init__(self, *args, **kwargs):
        super(BillingStorageForm, self).__init__(*args, **kwargs)
        total_cost = 0

        if self.action.type == 'M':  # If modify then get existing data
            instance_id = self.request.POST.get('instance_id')

            if instance_id:
                #if self.action.service.name == 'miStorage':
                si = self.vol.objects.get(id=instance_id)
                #else: # miBackup
                #    si = self.vol.objects.get(id=instance_id)
        
                self.fields["shortcode"].initial = si.shortcode
                self.fields["billingAuthority"].initial = 'yes'
                self.fields["serviceLvlAgreement"].initial = 'yes'

        if self.action.service.name == 'miBackup':
            descr = self.fields['totalCost'].description.replace('~', '47 per TB')
        else:
            option = StorageRate.objects.get(id=self.request.POST['selectOptionType'])

            #if self.action.service.name == 'miStorage':
            #    total_cost = option.get_total_cost(self.request.POST['sizeGigabyte'])
            #else:
            total_cost = option.get_total_cost(self.request.POST['size'])

            descr = self.fields['totalCost'].description.replace('~', str(total_cost))

        
        self.fields['totalCost'].description = descr

    def get_summary(self, *args, **kwargs):
        summary = super().get_summary(*args, **kwargs)

        if self.action.service.name == 'miStorage':
            option = StorageRate.objects.get(id=self.data['selectOptionType'])
            total_cost = option.get_total_cost(self.data['size'])
            summary.append({'label': 'Total Cost', 'value': str(total_cost)})

        instance_id = self.data.get('instance_id')
        
        if instance_id:
            si = self.vol.objects.get(id=instance_id)
            if self.data['shortcode'] != si.shortcode:
                summary[0]['label'] = '*' + summary[0]['label']
                    
        return summary


class VoicemailForm(TabForm):

    def __init__(self, *args, **kwargs):
        super(VoicemailForm, self).__init__(*args, **kwargs)

        if self.is_bound:
            action_id = self.request.POST.get('action_id')
        else:
            action_id = self.request.path[-2:]

        if action_id == '40':   # Add
            del(self.fields['cancelRebuild'])
            del(self.fields['pinOrPass'])
        elif action_id =='16':  # Reset Pin
            del(self.fields['cancelRebuild'])
        elif action_id =='15':  # Cancel/Rebuild
            del(self.fields['pinOrPass'])


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
