from django import forms
from django.forms import ModelForm
from .models import Product, Service, Action, Feature, FeatureCategory, FeatureType, Restriction, ProductCategory, Element, StorageInstance, Step
from pages.models import Page
from project.pinnmodels import UmOSCBuildingV


class McGroup(forms.CharField):
    widget = forms.EmailInput
    #default_validators = [validators.validate_email]

    def __init__(self, **kwargs):
        super().__init__(strip=True, **kwargs)

class TabForm(forms.Form):

    template = 'order/base_form.html'

    def get_next_tab(self, action_id):

        step = Step.objects.get(name='detailsNFS')
        next_tab = TabForm(step)
        print('show')
        return next_tab

    def get_summary(self, visible):

        summary = []

        for key, value in self.cleaned_data.items():
            #print('klist', key)
            field = self.fields[key]

            if key in visible:  # Add visible fields to the review page
                if hasattr(field, 'choices'):
                    for choice in field.choices:
                        if choice[0] == value:
                            value = choice[1]

                #print(field.label,'~', value)
                summary.append({'label': field.label, 'value': value})

        return summary

    def is_valid(self):
        valid = super(TabForm, self).is_valid()
        return valid

    def __init__(self, tab, *args, **kwargs):
        super(TabForm, self).__init__(*args, **kwargs)
    #def __init__(self, tab, *args, **kwargs):
    #    super(TabForm, self, *args, **kwargs).__init__()
        self.tab_name = tab.name
        element_list = Element.objects.all().filter(step_id = tab.id).order_by('display_seq_no')

        for element in element_list:

            if element.type == 'Radio':
                field = forms.ChoiceField(choices=eval(element.attributes), widget=forms.RadioSelect(attrs={'class': 'form-control'}))
                field.template_name = 'project/radio.html'
            elif element.type == 'Chart':
                field = forms.ChoiceField(label=element.label, help_text=element.description
                                        , widget=forms.Select(attrs={'class': "form-control"}), choices=Chartcom.get_user_chartcoms(request.user.id))
                                                                        #AuthUserDept.get_order_departments(request.user.id)
                field.dept_list = Chartcom.get_user_chartcom_depts(request.user.id) #['12','34','56']
            elif element.type == 'NU':
                field = forms.ChoiceField(widget=forms.NumberInput(attrs={'min': "1"}))
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
            else:
                print('use globals', element.type)
                field = globals()[element.type]
                field.field_name = element.name
                field.template_name = 'project/text.html'
                #field = forms.IntegerField(label=element.label, help_text=element.description)

            field.name = element.name
            #print(field.name)
            field.label = element.label
            field.help_text = element.help_text
            field.description = element.description
            field.attributes = element.attributes
            field.display_seq_no = element.display_seq_no
            field.display_condition = element.display_condition
            field.type = element.type

            self.fields.update({element.name: field})


class BillingForm(TabForm):

    def get_summary(self, postdata):
        return 'override data'


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
    TRUE_FALSE_CHOICES = (
    (True, 'Yes'),
    (False, 'No')
    )

    contact_yn = forms.ChoiceField(choices = TRUE_FALSE_CHOICES, label="Are you the on site contact?", required=True)
    contact_yn.type = 'Radio'

    contact_id = forms.CharField(label='Uniqname of the on site contact person', max_length=8)

    contact_name = forms.CharField(label='Name of the on site contact person', max_length=40)
    contact_number = forms.CharField(label='Best number to contact', max_length=10)
    comments = forms.CharField(label='Comments', required=False, widget=forms.Textarea(attrs={'cols':'100', 'class':'form-control'}) )
    file = forms.FileField(label="Please attach any drawings, spreadsheets or floor plans with jack locations as needed", required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
    template = 'order/dynamic_form.html'

class VolumeSelectionForm(TabForm):
    template = 'order/volume_selection.html'

    volume_list = StorageInstance.objects.all()


class DetailsCIFSForm(TabForm):
    template = 'order/cifs_details.html'


class AccessCIFSForm(TabForm):
    template = 'order/cifs_access.html'


class DetailsNFSForm(TabForm):
    template = 'order/nfs_details.html'


class AccessNFSForm(TabForm):
    template = 'order/nfs_access.html'


class BillingStorageForm(TabForm):
    template = 'order/billing_storage.html'


class VoicemailForm(TabForm):
    template = 'order/voicemail.html'


class ContactCenterForm(TabForm):
    phone_number = forms.CharField(label='summary', max_length=12)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols':'100'}) )

    template = 'order/contact_center.html'


class ReviewForm(TabForm):
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
