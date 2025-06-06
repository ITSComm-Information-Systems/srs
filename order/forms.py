from django import forms
from django.core import validators
#from django.db.models.fields import IntegerField
from django.forms import ModelForm, formset_factory
#from .models import Product, Service, Action, Feature, FeatureCategory, FeatureType, Restriction, ProductCategory, Element, StorageInstance, Step, StorageMember, StorageHost, StorageRate
from .models import *
from softphone.models import Category
from pages.models import Page
from project.pinnmodels import UmOSCBuildingV, UmMpathDwCurrDepartment
from oscauth.models import LDAPGroupMember
from project.integrations import MCommunity, create_ticket_database_modify, Zoom
import math
from project.models import Choice

from project.forms.fields import *

get_choices = Choice.objects.get_choices

def get_storage_options(action):
    opt_list = []
    for opt in StorageRate.objects.filter(type=action.override['storage_type'], service=action.service, display_seq_no__lt=100):
        rate = round(opt.rate,2)
        if opt.rate != rate: 
            rate = str(opt.rate).rstrip('0')
        label = f'{opt.label} (${rate} / per {opt.unit_of_measure} per month)'
        opt_list.append((opt.id, label))

    return opt_list

def get_softphone_categories():
    cat_list = []
    for cat in Category.objects.filter(sequence__isnull=False).exclude(sequence__in=(8,9)).order_by('sequence'):
        cat_list.append((cat.code, cat.label))

    return cat_list

class TabForm(forms.Form):

    template = 'order/base_form.html'

    def set_initial(self, instance_id):
        vol = self.vol.objects.get(id=instance_id)
        self.instance = vol

        for fieldname, field in self.fields.items():
            if type(field) == forms.MultipleChoiceField:
                cb = vol.get_checkboxes()
                if 'multi_protocol' in cb:
                    cb.remove('multi_protocol')
                field.initial = cb # vol.get_checkboxes()


            elif fieldname == 'owner':
                field.initial = vol.owner.name

            elif fieldname == 'mCommunityName':
                field.initial = vol.owner.name

            elif hasattr(vol, fieldname):
                field.initial = getattr(vol,fieldname)

            elif fieldname == 'selectOptionType':
                if vol.rate.display_seq_no > 99:
                    label = f'{vol.rate.label} (${vol.rate.rate} / per {vol.rate.unit_of_measure} per month)'
                    self.fields["selectOptionType"].choices = [(vol.rate.id, label,)]

                field.initial = str(vol.rate_id)
            
            if fieldname == 'sensitive_regulated':
                if vol.sensitive_regulated:
                    field.initial = 'yessen'
                else:
                    field.initial = 'nosen'



    def clean(self):
        if 'oneTimeCharges' in self.cleaned_data:
            if self.cleaned_data['oneTimeCharges'] == '11':                    
                self.add_error('oneTimeCharges', 'You must select a chartcom')

        if self.action.service.id == 10:  # Locker
            if 'size' in self.cleaned_data:
                if self.cleaned_data['size'] < 10:
                    self.add_error('size', 'Enter a size of at least 10 terabytes') 

        if self.action.service.id == 11:  # Data Den
            if 'size' in self.cleaned_data:
                if self.cleaned_data['size'] < 5:
                    self.add_error('size', 'Enter a size of at least 5 terabytes') 

        if 'name' in self.cleaned_data and self.action.service.id in [9,10,11]:  # ARC Instance Name check
            name = self.cleaned_data['name']
            if name and 'name' in self.changed_data:
                if self.action.service.id == 9:  # Turbo must be unique within Turbo
                    instance = ArcInstance.objects.filter(name__iexact=name,service_id=9).select_related('service')                
                else:  # Data Den and Locker Need to be unique across the two services.
                    instance = ArcInstance.objects.filter(name__iexact=name,service_id__in=[10,11]).select_related('service')

                if len(instance) > 0:
                    service = instance[0].service.label
                    self.add_error('name', f'A {service} volume named {name.lower()} already exists. Please choose a different name.')

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
 
                if field.type == 'Radio' or field.type == 'Select':
                    for choice in field.choices:
                        if isinstance(choice[1], str):
                            if str(choice[0]) == value:
                                value = choice[1]
                                break
                        else:  # Search Optgroup
                            for choice in choice[1]:
                                if str(choice[0]) == value:
                                    value = choice[1]
                                    break

                if field.type == 'Checkbox':  
                    label = field.choices[0][1]
                    if len(field.choices) > 1:  # Process list of options
                        label = field.label
                        selections = []
                        for choice in field.choices:
                            if str(choice[0]) in value:
                                selections.append(choice[1])
                        
                        value = selections
                    elif len(value) > 0:  
                        value = 'Yes'
                    else:
                        value = 'No'

                if field.type == 'List':  
                    value_list = self.data.getlist(key)
                    value = ', '.join(value_list)

                if self.action.type == 'M':

                    if key in ['billingAuthority', 'serviceLvlAgreement']:
                        pass

                    elif key == 'nodeNames' or key == 'backupTimes':

                        new = {}
                        for node in self.node_list:
                            new[node['name']] = node['time']+' '+node['ampm']

                        old = {}
                        removed = []
                        for node in BackupNode.objects.filter(backup_domain=self.instance.id):
                            old[node.name] = node.time
                            if node.name not in new:
                                removed.append(node.name)
                        
                        if old != new:
                            label = '*' + label

                        value = ''
                        for node, time in new.items():
                            if node in old:
                                if time == old[node]:
                                    value = value + f'{node}@{time}, '
                                else:
                                    value = value + f'{node}@{time}*, '
                            else:
                                value = value + f'[{node}@{time}], '

                        if removed:
                            value = value + ' (REMOVED:'+', '.join(removed)+')'

                    elif key == 'permittedHosts':
                        new = set(self.request.POST.getlist('permittedHosts'))
                        old = set()
                        for host in self.instance.get_hosts():                        
                            old.add(host.name)
                        new.remove('')
                        if old != new:
                            label = '*' + label 
                            existing=[]
                            toadd=[]
                            removed=[]
                            for r in old:
                                if r not in new:
                                    removed.append(r)
                            for x in new:
                                if x not in old:
                                    toadd.append('['+x+']')
                                else:
                                    existing.append(x)
                            value=', '.join(existing)+', '+', '.join(toadd)

                            if removed:
                                value = value + ' (REMOVED:'+', '.join(removed)+')'

                    elif key == 'shortcode' and hasattr(self, 'shortcode_list'):
                        new = set()
                        for sc in self.shortcode_list:
                            tup = (sc['shortcode'], int(sc['size']))
                            new.add(tup)

                        old = set()
                        for sc in self.instance.get_shortcodes():
                            old.add((sc.shortcode, sc.size))

                        if old != new:
                            label = '*' + label

                    elif key == 'versions_after_delet' or key == 'versions_while_exist':
                        old = int(self.fields[key].initial)
                        new = self.cleaned_data[key]
                        if old != new:
                            label = '*' + label                            

                    elif key in self.changed_data:
                        label = '*' + label

                if isinstance(value, list):
                    nl = ', '
                    inline = nl.join(value)
                    summary.append({'name': getattr(field, 'name', '-'), 'label': label, 'value': '', 'list': value, 'inline': inline})
                else:
                    summary.append({'name': getattr(field, 'name', '-'), 'label': label, 'value': value})

        return summary

    def __init__(self, tab, action, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TabForm, self).__init__(*args, **kwargs)




        if action.service.id == 7:
            self.vol = StorageInstance
            self.host = StorageHost
        elif action.service.id == 8:
            self.vol = BackupDomain
        elif action.service.id == 13:
            self.vol = Server
        elif action.service.id == 14:
            self.vol = Database
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
                field = forms.IntegerField(widget=forms.NumberInput(attrs={'min': "1", 'class': 'form-control'}), **element.arguments)
                field.template_name = 'project/number.html'
            elif element.type == 'Select':
                field = forms.ChoiceField(choices=eval(element.attributes), widget=forms.Select(attrs={'class': 'form-control'}))
                #field.initial = element.attributes
                field.template_name = 'project/text.html'
            elif element.type == 'ST' or element.type == 'List':
                field = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), **element.arguments)
                field.template_name = 'project/text.html'
                if element.attributes:
                    field.widget.input_type = element.attributes
            elif element.type == 'Checkbox':
                field = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), choices=eval(element.attributes), **element.arguments)
                field.template_name = 'project/checkbox.html'
            elif element.type == 'HTML':
                field = forms.CharField(required=False)
                field.template_name = 'project/static.html'
            elif element.type == 'McGroup--':
                field = McGroup()
                field.template_name = 'project/static.html'
            elif element.type == 'MyGroups':
                group_list = MCommunity().get_groups(self.request.user.username)

                choice_list = [(None, '---')]
                for group in group_list:
                    choice_list.append((group, group,))

                field = forms.ChoiceField(choices=choice_list, widget=forms.Select(attrs={'class': 'form-control'}))
                #field.initial = element.attributes
                field.template_name = 'project/text.html'
            elif hasattr(forms, element.type):
                fld = getattr(forms, element.type)
                field = fld(**element.arguments)
                field.widget.attrs={'class': 'form-control'}
                field.template_name = 'project/text.html'

            else:
                # Use custom field from project.forms.fields
                field = globals()[element.type](label=element.name)
                #field.field_name = element.name
                field.template_name = 'project/text.html'
                #field = forms.IntegerField(label=element.label, help_text=element.description)

            if element.attributes == 'optional':
                field.required = False

            if not hasattr(field, 'template_name'):
                field.template_name = 'project/text.html'

            field.name = element.name
            field.current_user = self.request.user
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

        if self.is_bound:
            try:
                vis = self.request.POST['visible']
                visible = vis.split(',')
                
                for field in self.fields:
                    if field not in visible:
                        self[field].field.required = False
            except:
                print('error checking visible')



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


class ChangeSFUserForm(TabForm):
    building_list = UmOSCBuildingV.objects.all()
    template = 'order/change_user.html'


class RestrictionsForm(TabForm):
    res = Restriction.objects.all()
    list = FeatureCategory.objects.all()

    for cat in list:
        cat.res = res.filter(category=cat).order_by('display_seq_no')
        last = cat.res.count()
        cat.last = cat.res[last-1].id

    information = Page.objects.get(permalink='/restriction')

    template = 'order/restrictions.html'


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True  # Django 4.1.9 workaround


class AddlInfoForm(TabForm):

    file = forms.FileField(label="Please attach any drawings, spreadsheets or floor plans with jack locations as needed", required=False, widget=MultipleFileInput(attrs={'multiple': True}))
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
        service = Action.objects.get(id=self.request.POST.get('action_id')).service
        if service.id == 13:
            label = 'Server'
        elif service.id == 14:
            label = 'Database'
        else:
            label = 'Volume'

        if self.data.get('volaction') == 'Delete':
            summary = [{'label': f'Are you sure you want to delete this {label}?', 'value': ''}
                        ,{'label': f'{label} Name:', 'value': instance.name}
                        ,{'label': 'Owner:', 'value': instance.owner.name}]
        else:
            summary = [{'label': f'{label} Name:', 'value': instance.name}]

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
                if service.id == 7:
                    self.volume_list = self.vol.objects.filter(service=service, type=vol_type, owner__in=groups).order_by('name').select_related('rate','owner','service')
                elif service.id in [9,10,11]:
                    self.template = 'order/turbo_volume_selection.html'
                    self.volume_list = ArcInstance().get_user_volumes(self.request.user, vol_type, service.id)
                else:  #Prefetch shortcodes
                    self.volume_list = self.vol.objects.filter(service=service, type=vol_type, owner__in=groups).order_by('name').select_related('rate','owner','service').prefetch_related('shortcodes')
                return
            elif service.id == 13:
                self.volume_list = self.vol.objects.filter(owner__in=groups, in_service=True).order_by('name').select_related('owner')
                self.detail = [{'name': 'CPU', 'quantity': 2, 'cost': 14.33},{'name': 'RAM', 'quantity': 4, 'cost': 4.20},{'name': 'DISK', 'quantity': 55, 'cost': 1.69}]
                self.cost_types = ['CPU', 'RAM', 'QUANTITY']

                if self.action.label.startswith('Review'):
                    self.template = 'order/server_review.html'
                else:
                    self.template = 'order/server_modify.html'
            elif service.id == 14:
                self.volume_list = self.vol.objects.filter(owner__in=groups, in_service=True, server__isnull=True).order_by('name')
                self.server_list = Server.objects.filter(owner__in=groups, in_service=True, database_type__isnull=False).order_by('name')

                if self.action.label.startswith('Review'):
                    self.template = 'order/database_review.html'
                else:
                    self.template = 'order/database_modify.html'
            elif service.id == 9:
                self.volume_list = self.vol.objects.filter(service=service, owner__in=groups).order_by('name').select_related('rate','owner','service').prefetch_related('shortcodes')
                #self.volume_list = self.vol.objects.filter(service=service, owner__in=groups).order_by('name')
                self.template = 'order/volume_review_turbo.html'
                for volume in self.volume_list:
                    self.total_cost = self.total_cost + volume.total_cost
                return
            elif service.id == 11:
                self.volume_list = ArcInstance().get_user_volumes(self.request.user, 'NFS', service.id)     
                self.template = 'order/volume_review.html'
                for volume in self.volume_list:
                   self.total_cost = self.total_cost + volume['total_cost']
                return
            else:
                self.volume_list = self.vol.objects.filter(service=service, owner__in=groups).order_by('name')
                self.template = 'order/volume_review.html'

            for volume in self.volume_list:
                self.total_cost = self.total_cost + volume.total_cost
                volume.shortcode_list = volume.get_shortcodes()


class AccessNFSForm(TabForm):
    template = 'order/nfs_access.html'

    notice3 = Page.objects.get(permalink='/notice/3')
 
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
                self['ad_group'].field.required = False

        #TODO Set checkboxes
        #self.fields['hipaaOptions'].initial == ['armis','globus_phi']

    def __init__(self, *args, **kwargs):
        super(DetailsNFSForm, self).__init__(*args, **kwargs)

        if self.is_bound:
            if 'multi_protocol' in self.data:
                if self.data['multi_protocol'] == 'ncifs':
                    self['ad_group'].field.required = False

        if 'flux' in self.fields:
            self['flux'].field.required = False

        if 'great_lakes' in self.fields:
            self['great_lakes'].field.required = False

        if 'hipaaOptions' in self.fields:
            if self.request.POST.get('sensitive_regulated') == 'nosen': 
                self['nonHipaaOptions'].field.required = False
                self.fields.pop('hipaaOptions')

            if self.request.POST.get('sensitive_regulated') == 'yessen': 
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


class DatabaseTypeForm(TabForm):
    template = 'order/database_type.html'


    def __init__(self, *args, **kwargs):
        super(DatabaseTypeForm, self).__init__(*args, **kwargs)

        self.fields['size'].widget.attrs.update({'step': 10})


    def clean(self):
        size = self.cleaned_data.get('size', 0)
        if size % 10 != 0:
            self.add_error('size', 'Disk size must be in increments of 10 Gigabytes.')

        if self.is_valid() and self.request.POST.get('shared') == 'Dedicated':
            self.fields['size'].widget.attrs.update({'data-server': 99})
            raise ValidationError("Selections require dedicated server")

        super().clean()


class DatabaseConfigForm(TabForm):

    def __init__(self, *args, **kwargs):
        super(DatabaseConfigForm, self).__init__(*args, **kwargs)

        try:
            if not Choice.objects.get(id=self.request.POST.get('midatatype')).code == 'MYSQL':
                self.fields.pop('url') 
        except:
            print('error getting database type')

        type = self.request.POST.get('midatatype')
        if type == '66':  # MSSQL
            self.fields['name'].validators = [validators.RegexValidator(
                    regex='^[a-zA-Z0-9_-]*$',
                    message='Name can contain letters, numbers, hypens, and underscores.',
                    code='invalid_name')]
        else:
            self.fields['name'].validators = [validators.RegexValidator(
                    regex='^[a-z0-9_]*$',
                    message='Name can contain lowercase letters, numbers, and underscores.',
                    code='invalid_name')]





class ServerInfoForm(TabForm):
    template = 'order/base_form.html'

    def __init__(self, *args, **kwargs):
        super(ServerInfoForm, self).__init__(*args, **kwargs)

        mc = MCommunity()
        hr = mc.get_user(self.request.user.username)   #EXEC_VP_MED_AFF
        michmed = False
        self.fields['michmed_flag'].initial = 'No'

        for afil in hr['umichHR']:
            if afil.find('deptVPArea=EXEC_VP_MED_AFF') > 0:
                michmed = True
                self.fields['michmed_flag'].initial = 'Yes'
                break

        if len(hr['umichHR']) > 1 and michmed:   # Hide field unless user has multiple appointments
            print('ask')
        else:
            self.fields['michmed_flag'].widget = forms.HiddenInput()
            self.fields['michmed_flag'].label = ' '          

        if self.request.method == 'GET':
            type = self.request.GET.get('type', None)
            #version = self.request.GET.get('version', None)
            size = self.request.GET.get('size', None)
        else:
            type = self.request.POST.get('database', None)
            #version = self.request.POST.get('version', None)
            size = self.request.POST.get('size', None)

        if type:
            self.fields['database'].widget.attrs.update({'readonly': True})
            self.fields['database'].initial = type
            self.fields['size'].widget.attrs.update({'readonly': True}) 
            self.fields['size'].initial = size
            #self.fields.pop('misevexissev')
            self.fields['ad_group'].initial = 'MiDatabase Support Team'
            self.fields['ad_group'].widget.attrs.update({'readonly': True})
        else:
            self.fields.pop('size') 
            self.fields.pop('database') 
            self.fields.pop('ad_group') 

    def get_summary(self, *args, **kwargs):
        summary = super().get_summary(*args, **kwargs)
        for rec in summary:
            if rec.get('name') == 'owner':
                email = MCommunity().get_group_email(rec['value'])
                if email:
                    rec['value'] = rec['value'] + ' | ' + email

        return summary
        
class ServerSupportForm(TabForm):
    template = 'order/server_support.html'

    def __init__(self, *args, **kwargs):
        super(ServerSupportForm, self).__init__(*args, **kwargs)

        self.fields['support_phone'].validators = [validators.RegexValidator(
                regex='^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$',
                message='Please provide a 10 digit phone number.',
                code='invalid_username')]

        if self.action.service.name=='midatabase':
            self.fields.pop('backup_time')
            self.fields.pop('patch_day')
            self.fields.pop('patch_time')
            self.fields.pop('reboot_day')
            self.fields.pop('reboot_time')
            return

        if hasattr(self, 'instance'):
            self.initial = self.instance.__dict__
            self.initial['patch_day'] = str(self.instance.patch_day_id)
            self.initial['patch_time'] = str(self.instance.patch_time_id)
            self.initial['reboot_day'] = str(self.instance.reboot_day_id)
            self.initial['reboot_time'] = str(self.instance.reboot_time_id)
            self.initial['backup_time'] = str(self.instance.backup_time_id)
            self.initial['on_call'] = str(self.instance.on_call)

        instance_id = self.request.POST.get('instance_id')
        if hasattr(self, 'instance') and not self.is_bound:
            for field in ['patch_day','patch_time','reboot_day','reboot_time','backup_time']:
                choice = getattr(self.instance, field)
                if choice:
                    self.fields[field].initial = choice.id

        if instance_id:
            server = Server.objects.get(id=instance_id)
            os_id = server.os_id
            if not server.managed:
                mang = 'unmang'
            else:
                mang = 'mang'
                
        else:
            mang = None
            server = None
            os_id = None
            db = None

        if self.request.POST.get('production') == 'False':
            self.fields['on_call'].initial = '0'
            self.fields['on_call'].disabled = True

        if self.request.POST.get('database'):
            db = self.request.POST.get('database')
            if db == 'MSSQL':
                name = self.request.POST.get('name')
                beginning_letter = name[3].lower()
                if 'a'<= beginning_letter  <= 'l':
                    self.fields['backup_time'].initial = Choice.objects.get(parent__code='SERVER_BACKUP_TIME', code='2200').id
                else:
                    self.fields['backup_time'].initial = Choice.objects.get(parent__code='SERVER_BACKUP_TIME', code='0000').id
                windows = True
                self.fields['backup_time'].disabled = True
                self.fields['backup_time'].label = "OS Daily Backup Time"
                self.fields['patch_day'].disabled = True
                self.fields['patch_day'].initial = Choice.objects.get(parent__code='SERVER_PATCH_DATE', code='SAT').id
                self.fields['patch_time'].disabled = True
                self.fields['patch_time'].initial = Choice.objects.get(parent__code='SERVER_PATCH_TIME', code='0500').id
            else:
                windows = False
        else:
            os = kwargs['request'].POST.get('misevos', os_id)
            os = Choice.objects.get(id=os).label

            if os.startswith('Windows'):
                windows = True
            else:
                windows = False

        if windows:
            # Remove specific choices from the patch_day field
            patch_days_to_remove = ['Monday', 'Tuesday', 'Wednesday']
            self.fields['patch_day'].choices = [
                choice for choice in self.fields['patch_day'].choices
                if choice[1] not in patch_days_to_remove
            ]
        else:
            if self.fields.get('reboot_day'):
                self.fields.pop('reboot_day')
            if self.fields.get('reboot_time'):
                self.fields.pop('reboot_time')

        if kwargs['request'].POST.get('managed', mang) == 'unmang' or kwargs['request'].POST.get('managed') == 'False':
            if self.fields.get('patch_day'):
                self.fields.pop('patch_day')
            if self.fields.get('patch_time'):
                self.fields.pop('patch_time')
            if self.fields.get('reboot_day'):
                self.fields.pop('reboot_day')
            if self.fields.get('reboot_time'):
                self.fields.pop('reboot_time')

        if kwargs['request'].POST.get('backup') == 'False':
            self.fields.pop('backup_time')
            
    def clean_reboot_time(self):
        patch_time_map = {
            '38':1,
            '39':3,
            '40':5,
            '41':7,
            '49':11
        }

        patch_day_map = {
            '363': 'MONDAY',
            '362': 'TUESDAY',
            '361': 'WEDNESDAY',
            '96': 'THURSDAY',
            '97': 'FRIDAY',
            '98': 'SATURDAY',
            '99': 'SUNDAY'
        }

        reboot_time_map = {
            '51':0,
            '52':0.5,
            '53':1,
            '54':1.5,
            '55':2,
            '56':2.5,
            '57':3,
            '58':3.5,
            '59':4,
            '60':4.5,
            '61':5,
            '62':5.5,
            '63':6,
            '64':6.5,
        }

        reboot_day_map = {
            '101': 'NONE',
            '102': 'DAILY',
            '103': 'SUNDAY',
            '104': 'MONDAY',
            '105': 'TUESDAY',
            '106': 'WEDNESDAY',
            '107': 'THURSDAY',
            '108': 'FRIDAY',
            '109': 'SATURDAY'
        }

        error = False

        reboot_day = self.cleaned_data.get('reboot_day')
        reboot_time = self.cleaned_data.get('reboot_time')
        patch_day = self.cleaned_data.get('patch_day')
        patch_time = self.cleaned_data.get('patch_time')

        #This checks that a reboot isnt scheduled early morning the following day if patch time is at 11pm
        # Check if patch_time is '49'(11pm) and reboot_time is one of '51', '52', or '53'(12:00am, 12:30am, 1:00am the following day)
        if patch_time == '49' and reboot_time in ['51', '52', '53']:
            # Check if the combination of patch_day and reboot_day matches any of the specified tuples
            if (patch_day, reboot_day) in [('96', '108'), ('97', '109'), ('98', '103'), ('99', '104')]:
                # Set the error flag to True if the conditions are met
                error = True

        # Check if the corresponding values exist in both the reboot_day_map and patch_day_map
        if reboot_day_map.get(reboot_day) and patch_day_map.get(patch_day):
            # Check if the values for reboot_day and patch_day match
            if reboot_day_map[reboot_day] == patch_day_map[patch_day]:
                # Check if patch_time is one of the specified values
                if patch_time in ['38', '39', '40', '41']:
                    # Calculate the time difference between patch_time and reboot_time
                    time_difference = patch_time_map[patch_time] - reboot_time_map[reboot_time]
                    # Check if the time difference is within the desired range
                    if -2 <= time_difference <= 0:
                        # Set the error flag to True if all conditions are satisfied
                        error = True

        if error:
            raise ValidationError("Reboot time cannot be within 2 hours of patch time.")
        super().clean()

        return reboot_time

class ServerDataForm(TabForm):
    template = 'order/server_data.html'

    def clean(self):

        if self.request.POST.get('managed') == 'False':
            if self.request.POST.get('misevregu') == 'True':
                raise ValidationError("Please select a managed server for sensitive data.")
            if self.request.POST.get('misevnonregu') == 'True':
                raise ValidationError("Please select a managed server for sensitive data.")

        super().clean()


class DiskForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField()
    name.widget.attrs.update({'class': 'form-control col-2', 'readonly': True})  

    size = forms.IntegerField(initial=10)
    size.widget.attrs.update({'class': 'form-control disk-size validate-integer', 'step': 10, 'min': '10'})  

    uom = forms.ChoiceField(choices=(('GB','GB'),('TB','TB')))
    uom.widget.attrs.update({'class': 'form-control disk-uom'})  

    class Meta:
        model = ServerDisk
        fields = ['id', 'name', 'size']

    def clean(self):

        current_size = self.initial.get('size')
        if current_size:
            if self.cleaned_data.get('size', 0) < current_size:
                if self.cleaned_data.get('uom') != 'TB':
                    self.add_error('size', f'Disk size cannot be decreased. Select a size of {current_size} or more.')

        if self.cleaned_data.get('uom') == 'GB' and self.cleaned_data.get('size', 0) < 1000:
            if self.cleaned_data.get('size', 0) % 10 != 0:
                self.add_error('size', 'Disk size must be in increments of 10 Gigabytes.')
            elif self.cleaned_data.get('name') == 'disk0' and self.cleaned_data.get('size', 0) < 50:
                self.add_error('size', f'Disk 0 must be 50 GB or more.')

        elif self.cleaned_data.get('uom') == 'TB' and self.cleaned_data.get('size', 0) > 10:
            self.add_error('size', 'Disk size must be 10 TB or less.')            

        super().clean()


class DiskDisplayForm(forms.ModelForm):
    name = forms.CharField()
    name.widget.attrs.update({'class': 'form-control col-2', 'readonly': True})  

    size = forms.IntegerField(min_value=1, initial=10)
    size.widget.attrs.update({'class': 'form-control disk-size', 'readonly': True})  

    uom = forms.ChoiceField(choices=(('GB','GB'),('TB','TB')))
    uom.widget.attrs.update({'class': 'form-control', 'readonly': True})  

    class Meta:
        model = ServerDisk
        fields = ['id', 'name', 'size']


class ServerSpecForm(TabForm):
    template = 'order/server_spec.html'

    uom_list = ['GB','TB']
    DiskFormSet = formset_factory(DiskForm, extra=0)
    DiskDisplayFormSet = formset_factory(DiskDisplayForm, extra=0)
    size_edit = forms.IntegerField(widget=forms.HiddenInput(), required=False, initial=0)

    for rate in StorageRate.objects.filter(name__startswith='SV-'):
        if rate.name == 'SV-RAM':
            ram_rate = rate.rate
        elif rate.name == 'SV-DI-REP':
            disk_replicated = rate.rate
        elif rate.name == 'SV-DI-NONREP':
            disk_no_replication = rate.rate
        elif rate.name == 'SV-DI-BACKUP':
            disk_backup = rate.rate

    def __init__(self, *args, **kwargs):
        super(ServerSpecForm, self).__init__(*args, **kwargs)

        if hasattr(self, 'instance'):
            self.initial = self.instance.__dict__
            self.initial['backup'] = str(self.instance.backup)
            self.initial['replicated'] = str(self.instance.replicated)
            self.initial['production'] = str(self.instance.production)

            if 'indows' in self.instance.os.label:  # Managed Linux can't edit disk
                self.fields['size_edit'].initial = 1
            elif 'anaged' not in self.instance.os.label: 
                self.fields['size_edit'].initial = 1
        
        if self.request.POST.get('misevregu') == 'True':
            self.fields['backup'].initial = 'True'
            self.fields['backup'].disabled = True

            if '78' in self.request.POST.getlist('regulated_data', []): # Check for PCI Data (78)
                self.fields['replicated'].disabled = True
                self.fields['replicated'].initial = 'True'
                self.fields['managed'].disabled = True
                self.fields['managed'].initial = 'True'
                self.fields.pop('misevprefix')

        if self.request.POST.get('database'):
            self.set_database_defaults()
            if self.is_bound:
                self.disk_formset = self.DiskDisplayFormSet(self.request.POST)            
            else:
                self.disk_formset = self.DiskDisplayFormSet(initial=self.disk_list)
            return

        instance_id = self.request.POST.get('instance_id')

        if self.is_bound:
            self.disk_formset = self.DiskFormSet(self.request.POST, initial=ServerDisk.objects.filter(server_id=instance_id).order_by('name').values())
            #x = self.disk_formset.is_valid()
        elif self.request.POST.get('action_type') == 'M':        
            self.disk_formset = self.DiskFormSet(initial=ServerDisk.objects.filter(server_id=instance_id).order_by('name').values())
        else:
            self.fields['size_edit'].initial = 1
            self.disk_formset = self.DiskFormSet(initial=[{'num': 0, 'name': 'disk0', 'size': 50, 'uom': 'GB'}])
            self.fields['cpu'].initial = 1
            self.fields['managed'].initial = True

    def set_database_defaults(self):
        
        database = self.request.POST.get('database')
        database_size = self.request.POST.get('size')
        #database_version = self.request.POST.get('database_version')

        cpu = self.request.POST.get('cpu', 2)
        ram = self.request.POST.get('ram')
        if ram:
            ram = int(ram)
        else:
            ram = 4

        self.fields['misevos'].required = False
        self.fields['misevos'].disabled = True

        self.fields['diskSize'].required = False

        self.fields['managed'].required = False
        self.fields['managed'].disabled = True

        self.fields['managed'].initial = True
        self.fields['replicated'].initial = True

        
        self.fields['backup'].initial = 'True'
        self.fields['backup'].disabled = True

        self.fields['public_facing'].disabled = True
        self.fields['public_facing'].initial = False
        

        if database == 'MSSQL':
            self.fields['cpu'].widget.attrs.update({'data-server': 99, 'min': 2})
            self.fields['cpu'].initial = 2
            self.fields['misevos'].initial = 129 # Windows 2022 - Managed

            base_size = float(database_size) / 10
            fifteen_percent = math.ceil(base_size * .15) * 10
            thirty_percent = fifteen_percent * 2
            ##thirty_percent = math.ceil(base_size * .3) * 10
            if ram < 8:
                paging_disk = 60
            else:
                paging_disk = math.ceil((ram-8)/4) * 10 + 60  # Source: Dude, trust me.
                # =roundup((D45-8)/4)*10+60

            self.disk_list =[{'name': 'disk0', 'size': paging_disk, 'uom': 'GB', 'state': 'disabled'},
                                {'name': 'disk1', 'size': thirty_percent, 'uom': 'GB', 'state': 'disabled'},
                                {'name': 'disk2', 'size': database_size, 'uom': 'GB', 'state': 'disabled'},
                                {'name': 'disk3', 'size': fifteen_percent, 'uom': 'GB', 'state': 'disabled'},
                                {'name': 'disk4', 'size': fifteen_percent, 'uom': 'GB', 'state': 'disabled'}]

        #elif database == 'MYSQL':
        else:
            self.fields['cpu'].widget.attrs.update({'data-server': 99, 'min': 2})
            self.fields['cpu'].initial = 2
            self.fields['misevos'].initial = 341
            self.disk_list =[{'name': 'disk0', 'size': '50', 'uom': 'GB', 'state': 'disabled'},
                                {'name': 'disk1', 'size': database_size, 'uom': 'GB', 'state': 'disabled'},
                                {'name': 'disk2', 'size': database_size, 'uom': 'GB', 'state': 'disabled'}]

    def get_summary(self, *args, **kwargs):
        summary = super().get_summary(*args, **kwargs)

        for line in summary:
            if line['label'] == 'Server Name':
                line['value'] = self.data.get('name')

            #if line['label'] == 'Disk Space':
            #    break

        disk_review = []
        disk_size = 0

        #if self.disk_formset.is_valid:
        #    for disk in self.disk_formset.cleaned_data:
        #        disk_size = disk_size + int(disk['size'])
        #        disk_review.append(f"{disk['name']} {disk['size']} {disk['uom']} ")

        for form in self.disk_formset:
            changed = ''
            disk = form.cleaned_data
            if disk['uom'] == 'TB':
                disk_size = disk_size + int(disk['size']) * 1024
            else:
                disk_size = disk_size + int(disk['size'])

            if self.action.id == 71:
                if form.changed_data != ['uom']:
                    changed = '*'

            disk_review.append(f"{disk['name']} - {disk['size']} {disk['uom']} {changed}")

        summary.append({'label': 'Disk Space', 'value': disk_size, 'list': disk_review})
        #line['value'] = disk_size
        #line['list'] = disk_review

        return summary


    def clean(self):
        if not self.disk_formset.is_valid():
            self.add_error('diskSize', '')

        name = self.request.POST.get('name')
        

        if name:

            servername = Server.objects.filter(name__iexact=name)

            if len(servername) > 0:
                self.add_error('serverName', f'A server named {name.lower()} already exists. Please choose a different name.')

            import re
            if not re.match('^[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$', name):
                self.add_error('serverName', 'Name can contain letters, numbers, and single hypens.') 

            # managed windows name can't exceed 15 char:
            if len(name) > 15:
                if self.cleaned_data.get('managed') == 'True':
                    os = self.cleaned_data.get('misevos', False)
                    if os:
                        os_name = Choice.objects.get(id=int(os)).label
                        #if os_name.startswith('Windows'):
                        self.add_error('serverName', 'Server name cannot exceed 15 characters (including prefix).')

        ram = self.cleaned_data.get('ram', None)
        cpu = self.cleaned_data.get('cpu', None)
        if ram != None and cpu != None:
            if ram / cpu < 2:
                self.add_error('ram', 'Ram must be at least double cpu.')

            if self.action.type == 'M':
                if self.instance.managed and cpu < 2:
                    if self.instance.os.label.startswith('Windows'):
                        self.add_error('cpu', 'Managed Windows requires at least two cpu.')                        
                
            if cpu < 2 and self.cleaned_data.get('managed', False):
                os = self.cleaned_data.get('misevos', False)
                if os:
                    os_name = Choice.objects.get(id=int(os)).label
                    if os_name.startswith('Windows'):
                        self.add_error('cpu', 'Managed Windows requires at least two cpu.')
    
        production = self.cleaned_data.get('production', None)

        super().clean()  # When regular clean isn't enough


class DataDenForm(TabForm):
    template = 'order/accessCIFS.html'
    notice3 = Page.objects.get(permalink='/notice/3')


class DetailsCIFSForm(TabForm):
    template = 'order/accessCIFS.html'
    notice3 = Page.objects.get(permalink='/notice/3')


class BackupDetailsForm(TabForm):
    template = 'order/backup_details.html'
    notice3 = Page.objects.get(permalink='/notice/3')

    def __init__(self, *args, **kwargs):
        super(BackupDetailsForm, self).__init__(*args, **kwargs)

        self.time_list = eval(self.fields['backupTime'].attributes)
        self.ampm_list = ['AM','PM']
        
        if self.request.method == 'POST': # Skip for initial load on Add
            if self.is_bound:   # Reload Host list
                self.node_list = []
                nodes = self.data.getlist('nodeNames')
                times = self.data.getlist('backupTime')
                ampm = self.data.getlist('backupTimeampm')

                for count, node in enumerate(nodes):
                    if node:
                        self.node_list.append({'name': node, 'time': times[count], 'ampm':ampm[count]})
            else:
                instance_id = self.request.POST.get('instance_id')
                if instance_id: 
                    bd = BackupDomain.objects.get(id=instance_id)
                    self.fields["mCommunityName"].initial = bd.owner
                    self.fields["versions_while_exist"].initial = bd.versions_while_exists
                    self.fields["versions_after_delet"].initial = bd.versions_after_deleted
                    self.fields["days_extra_versions"].initial = bd.days_extra_versions
                    self.fields["days_only_version"].initial = bd.days_only_version

                    self.node_list = BackupNode.objects.filter(backup_domain=instance_id)
        else:
            self.node_list = []
            self.node_list.append({'name': '', 'time': ''})

    def get_summary(self, *args, **kwargs):
        summary = super().get_summary(*args, **kwargs)
        summary.pop(2) # Remove backupTime field from summary
        return summary

class BillingStorageForm(TabForm):

    def __init__(self, *args, **kwargs):
        super(BillingStorageForm, self).__init__(*args, **kwargs)
        total_cost = 0

        self.fields['shortcode'].validators=[validate_shortcode]

        if self.action.service.name=='lockerStorage' or self.action.service.name=='turboResearch' or self.action.service.name=='dataDen':
            self.template = 'order/billing_storage.html'
            self.shortcode_list = []

            if self.request.method == 'POST': # Skip for initial load on Add
                self.total_size = self.request.POST['size']
                if self.is_bound:   # Reload Shortcode list
                    shortcodes = self.data.getlist('shortcode')
                    terabytes = self.data.getlist('terabytes')
                    self.new_total_size = 0

                    for count, size in enumerate(terabytes):
                        if size != '0' or shortcodes[count]:
                            self.shortcode_list.append({'shortcode': shortcodes[count], 'size': size})
                            self.new_total_size = self.new_total_size + int(size)

            
            if len(self.shortcode_list) == 0:
                
                self.shortcode_list = [{'shortcode': '', 'size': self.total_size}]

        if self.action.type == 'M':  # If modify then get existing data
            instance_id = self.request.POST.get('instance_id')

            if instance_id:
                #if self.action.service.name == 'miStorage':
                si = self.vol.objects.get(id=instance_id)
                #else: # miBackup
                #    si = self.vol.objects.get(id=instance_id)
                if self.action.service.name=='lockerStorage' or self.action.service.name=='turboResearch' or self.action.service.name=='dataDen':
                    if not self.is_bound:
                        self.shortcode_list = si.get_shortcodes()

                else:
                    self.fields["shortcode"].initial = si.shortcode

                self.fields["billingAuthority"].initial = 'yes'
                self.fields["serviceLvlAgreement"].initial = 'yes'
    
                if self.action.service.name in ['turboResearch','dataDen']:
                    if hasattr(si, 'research_computing_package'):
                        if si.research_computing_package == True:
                            self.fields["research_comp_pkg"].initial = 'yes'

        if self.action.service.name == 'miBackup':
            rate = StorageRate.objects.get(name=BackupDomain.RATE_NAME)
            descr = self.fields['totalCost'].description.replace('~', f'{round(rate.rate,2)} per {rate.unit_of_measure}')
        elif self.action.service.name == 'dataDen':
            option = StorageRate.objects.get(id=28)
            total_cost = option.get_total_cost(self.request.POST['size'])
            descr = self.fields['totalCost'].description.replace('~', str(total_cost))
        elif self.action.service.name == 'midatabase':
            descr = self.fields['totalCost'].description.replace('~', '0.00')
            self.fields['shortcode'].label = 'Enter Shortcode for departmental tracking purposes'
        elif self.action.service.name == 'miServer':
            total_cost = self.request.POST.get('total_cost', 0)
            descr = self.fields['totalCost'].description.replace('~', str(total_cost))
        else:
            option = StorageRate.objects.get(id=self.request.POST['selectOptionType'])

            #if self.action.service.name == 'miStorage':
            #    total_cost = option.get_total_cost(self.request.POST['sizeGigabyte'])
            #else:
            total_cost = option.get_total_cost(self.request.POST['size'])

            descr = self.fields['totalCost'].description.replace('~', str(total_cost))

        
        self.fields['totalCost'].description = descr

    def clean(self):
        super().clean()
        
        if self.action.service.name=='lockerStorage' or self.action.service.name=='turboResearch' or self.action.service.name=='dataDen':
            if int(self.total_size) != self.new_total_size:
                self.shortcode_error = f'Sizes must total {self.total_size}'
                self.add_error('totalCost', 'block') 
            else:
                for shortcode in self.shortcode_list:
                    sc = shortcode['shortcode']
    
                    try:
                        UmOscAllActiveAcctNbrsV.objects.get(short_code=sc)
                    except:
                        self.shortcode_error = f'Shortcode: {sc} not found.'
                        self.add_error('totalCost', 'block')       

    def get_summary(self, *args, **kwargs):
        summary = super().get_summary(*args, **kwargs)

        if self.action.service.name not in ['miBackup','midatabase']:
            if self.action.service.name == 'dataDen':
                option = StorageRate.objects.get(id=28)
            elif self.action.service.name == 'miServer':
                option = StorageRate.objects.get(id=1)
            else:
                option = StorageRate.objects.get(id=self.data['selectOptionType'])

            if self.action.service.name == 'miServer':
                total_cost = '$' + self.request.POST.get('total_cost', 0)
            else:
                total_cost = option.get_total_cost(self.data['size'])

            summary.append({'label': 'Total Monthly Cost', 'value': str(total_cost)})

        if self.action.service.name=='lockerStorage' or self.action.service.name=='turboResearch' or self.action.service.name=='dataDen':
            shortcode_list = self.data.getlist('shortcode')
            size_list = self.data.getlist('terabytes')
            label = ''
            for num, shortcode in enumerate(shortcode_list):
                if shortcode:
                    label = f'{label}   \n {size_list[num]}TB to {shortcode},'

            summary[0]['value'] = label 

        if self.action.service.name in ['turboResearch','dataDen']:
            summary[3]['label'] = 'I have read the Sensitive Data Guide, agree that my use of this service complies with those guidelines and accept the terms of the Service Level Agreement.'
        else:
            summary[2]['label'] = 'I have read the Sensitive Data Guide, agree that my use of this service complies with those guidelines and accept the terms of the Service Level Agreement.'


        #instance_id = self.data.get('instance_id')
        
        #if instance_id:
        #    si = self.vol.objects.get(id=instance_id)
        #    if self.data['shortcode'] != si.shortcode:
        #        summary[0]['label'] = '*' + summary[0]['label']
                    
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
    template = 'order/equipment.html'

    def __init__(self, *args, **kwargs):
        super(EquipmentForm, self).__init__(*args, **kwargs)

        if self.action.id == 77: # Zoom for Government
            self.cat = ['VOIP']
            self.cat[0] = Product.objects.all().filter(active=True, category=41).order_by('display_seq_no') # Zoom for Govt
            self.cat[0].id = 'voip'
        else:
            self.cat = ['Basic','VOIP']
            self.cat[0] = Product.objects.all().filter(active=True, category=1).order_by('display_seq_no')
            self.cat[0].id = 'basic'
            self.cat[1] = Product.objects.all().filter(active=True, category__in=[2, 4]).order_by('display_seq_no') # Voip and Conference
            self.cat[1].id = 'voip'


class ProductForm(TabForm):
    category_list = ProductCategory.objects.all().order_by('display_seq_no') 
    product_list = Product.objects.all().filter(active=True).order_by('category','display_seq_no') 
    template = 'order/products.html'


class PhoneLocationForm(TabForm):
    phone_number = forms.CharField(label='Current Phone Number')
    building = forms.CharField(label='Building', max_length=100)
    floor = forms.CharField(label='Floor', max_length=100)
    room = forms.CharField(label='Room', max_length=100)
    jack = forms.CharField(max_length=100)
    template = 'order/phone_location.html'

class DatabaseForm(ModelForm):

    size_choice = ((10, '10 GB'),(20, '20 GB'),(30, '30 GB'),(40, '40 GB'),(50, '50 GB'))
    size = forms.TypedChoiceField(coerce=int, label='Size', choices=size_choice)

    owner_name = forms.ChoiceField(label='Owner', widget=forms.Select(attrs={'class': 'form-control'}))    
    shortcode = forms.CharField(label='Shortcode', validators=[validate_shortcode])

    class Meta:
        model = Database
        fields = ('size','support_email','support_phone','shortcode')

    def __init__(self, user, *args, **kwargs):
        super(DatabaseForm, self).__init__(*args, **kwargs)
        self.user = user
        group_list = MCommunity().get_groups(user.username)

        choice_list = [(None, '---')]
        for group in group_list:
            choice_list.append((group, group,))

        self.fields['owner_name'].choices = choice_list
        self.fields['owner_name'].initial = self.instance.owner.name


    def clean(self):
        super().clean()

        for field in self.errors:
            self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})

    def save(self, *args, **kwargs):

        if 'owner_name' in self.changed_data:
            self.instance.owner = LDAPGroup().lookup( self.cleaned_data.get('owner_name') )
            #owner = LDAPGroup.lookup(self.cleaned_data.get('owner_name'))

        if self.has_changed() and self.changed_data != ['shortcode']:  # Gotta change more than shortcode to create ticket

            description = f'Name: {self.instance.name} \n'
            for key, value in self.cleaned_data.items():
                label = self.fields[key].label
                if key in self.changed_data:
                    value = f'{value}*'
                description = description + f'{label}:{value} \n'

            create_ticket_database_modify(self.instance, self.user, description)

        super().save(*args, **kwargs)  # Call the "real" save() method.


class AddSMSForm(forms.Form):
    uniqname = forms.CharField(label='Uniqname',
                               widget=forms.TextInput(attrs={'class': 'form-control'}),
                               help_text = 'Uniqname of zoom user.')

    def clean(self):
        zoom = Zoom().user_sms_elig(self.cleaned_data.get('uniqname'))
        if 'phone_numbers' in zoom:
            self.phone_numbers = [pn['number'][2:12] for pn in zoom.get('phone_numbers')]
            loc = UmOscServiceProfileV.objects.filter(service_number__in=self.phone_numbers)
            user_depts = AuthUserDept.get_order_departments(self.request.user.id).values_list('dept', flat=True)
            for loc in UmOscServiceProfileV.objects.filter(service_number__in=self.phone_numbers, service_type='VoIP'
                                                           , service_status_code='In Service'
                                                           , subscriber_status='Active'):
                if loc.deptid not in user_depts:
                    self.add_error('uniqname', f'No order access for dept {loc.deptid}.') 
                    self.fields['uniqname'].widget.attrs.update({'class': ' is-invalid form-control'})
                    self.phone_numbers = None
                    break
                
        else:
            self.add_error('uniqname', zoom.get('message')) 
            self.fields['uniqname'].widget.attrs.update({'class': ' is-invalid form-control'})

        super().clean()

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
            self.kwargs = kwargs.pop('request', None)
        super(AddSMSForm, self).__init__(*args, **kwargs)
