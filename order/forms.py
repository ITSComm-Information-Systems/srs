from django import forms
from django.forms import ModelForm
from .models import Product, Service, Action, Feature, FeatureCategory, FeatureType, Restriction, ProductCategory
from project.pinnmodels import UmOSCBuildingV

class FeaturesForm(forms.Form):
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


class RestrictionsForm(forms.Form):
    res = Restriction.objects.all()
    list = FeatureCategory.objects.all()

    for cat in list:
        cat.res = res.filter(category=cat).order_by('display_seq_no')
        last = cat.res.count()
        cat.last = cat.res[last-1].id

    template = 'order/restrictions.html'


class AddlInfoForm(forms.Form):
    TRUE_FALSE_CHOICES = (
    (True, 'Yes'),
    (False, 'No')
    )

    contact_yn = forms.ChoiceField(choices = TRUE_FALSE_CHOICES, label="Are you the on site contact?", required=True)
    contact_yn.type = 'Radio'
    contact_id = forms.CharField(label='Uniqname', max_length=8)
    contact_name = forms.CharField(label='Name', max_length=40)
    contact_number = forms.CharField(label='Best number to contact.', max_length=10)
    comments = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols':'100'}) )
    file = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))

    template = 'order/dynamic_form.html'


class ReviewForm(forms.Form):
    summary = forms.CharField(label='summary', max_length=6)
    template = 'order/review.html'


class AuthCodeForm(forms.Form):
    TYPE_CHOICES = (
    ('Individual', 'Individual'),
    ('Workgroup', 'Workgroup')
    )
    type = forms.ChoiceField(choices = TYPE_CHOICES, required=True)
    name = forms.CharField(label='summary', max_length=100)
    template = 'order/auth_code.html'

class CMCCodeForm(forms.Form):
    code = forms.CharField(label='CMC Code', max_length=100)
    template = 'order/cmc_code.html'


class NewLocationForm(forms.Form):
    building_list = UmOSCBuildingV.objects.all()
    new_building_code = forms.CharField(label='Building Code', max_length=100)
    new_building_name = forms.CharField(label='Building Name', max_length=100)
    new_floor = forms.CharField(label='Floor', max_length=100)
    new_room = forms.CharField(label='Room', max_length=100)

    template = 'order/location.html'


class EquipmentForm(forms.Form):
    cat = ['Basic','VOIP']
    cat[0] = Product.objects.all().filter(category=1).order_by('display_seq_no')
    cat[0].id = 'basic'
    cat[1] = Product.objects.all().filter(category__in=[2, 4]).order_by('display_seq_no') # Voip and Conference
    cat[1].id = 'voip'
    template = 'order/equipment.html'


class ProductForm(forms.Form):
    category_list = ProductCategory.objects.all().order_by('display_seq_no') 
    product_list = Product.objects.all().order_by('category','display_seq_no') 
    template = 'order/products.html'


class PhoneLocationForm(forms.Form):
    phone_number = forms.CharField(label='Current Phone Number')
    building = forms.CharField(label='Building', max_length=100)
    floor = forms.CharField(label='Floor', max_length=100)
    room = forms.CharField(label='Room', max_length=100)
    jack = forms.CharField(max_length=100)
    template = 'order/phone_location.html'
