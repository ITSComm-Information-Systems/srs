from django import forms
from django.forms import ModelForm
from .models import Product, Service, Action, Feature, Restriction


class FeaturesForm(forms.Form):
    features = forms.ModelMultipleChoiceField(
        queryset=Feature.objects.all(), 
        widget=forms.CheckboxSelectMultiple(),
    )
    list = Feature.objects.all()
    template = 'order/features.html'

    class Meta:
        model = Feature
        fields = ('name', 'description',) 

class PhoneForm(forms.Form):
    phone_number = forms.CharField(label='Phone')


class RestrictionsForm(forms.Form):
    restrictions = forms.ModelMultipleChoiceField(
        queryset=Restriction.objects.all(), 
        widget=forms.CheckboxSelectMultiple(),
    )
    list = Restriction.objects.all()
    #template = 'order/features.html'


class PhoneSetTypeForm(forms.Form):
    label = 'Phone Set Type'
    phone_types = [
    ('B', 'Basic'),
    ('A', 'Advanced'),
    ('I', 'IP'),
    ]

    purchase = forms.ChoiceField(label='Do you want to purchase equipment from ITCOM?', choices=[('yes','Yes'),
         ('no','No')], initial='yes', widget=forms.RadioSelect)
    byod = forms.CharField(label='Please enter the make and model of phone you will be using.', max_length=100)
    phone_set_type = forms.ChoiceField(choices=phone_types)

    template = 'order/phone_set_type.html'

class ChartfieldForm(forms.Form):
    occ = forms.CharField(label='OCC', max_length=6)
    mrc = forms.CharField(label='MRC', max_length=6)
    local = forms.CharField(label='Local', max_length=6)
    longdistance = forms.CharField(label='Long Distance', max_length=6)

class ReviewForm(forms.Form):
    contact = forms.BooleanField(label='Are you the on-site contact person?')
    contact_id = forms.CharField(label='Uniqname', max_length=8)
    contact_name = forms.CharField(label='Name', max_length=40)
    contact_number = forms.CharField(label='Best number to contact.', max_length=8)
    comments = forms.CharField(required=False, widget=forms.Textarea )
    file = forms.FileField(required=False)

class NewLocationForm(forms.Form):
    label = 'Location Form'
    campuses= [
    ('A', 'Ann Arbor'),
    ('F', 'Flint'),
    ('D', 'Dearborn'),
    ('O', 'Off site'),
    ]
    
    Campus = forms.ChoiceField(choices=campuses)
    building = forms.CharField(label='Building', max_length=100)
    floor = forms.CharField(label='Floor', max_length=100)
    room = forms.CharField(label='Room', max_length=100)


class EquipmentForm(forms.Form):
    equipment = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(), 
        widget=forms.RadioSelect,
    )
    list = Product.objects.all()
    template = 'order/products.html'


class LocationForm(forms.Form):
    label = 'Location Form'
    campuses= [
    ('A', 'Ann Arbor'),
    ('F', 'Flint'),
    ('D', 'Dearborn'),
    ]

    phone_number = forms.CharField(label='Current Phone Number')
    Campus = forms.ChoiceField(choices=campuses)
    building = forms.CharField(label='Building', max_length=100)
    floor = forms.CharField(label='Floor', max_length=100)
    room = forms.CharField(label='Room', max_length=100)


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description']