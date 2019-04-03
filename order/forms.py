from django import forms
from django.forms import ModelForm
from .models import Product, Service, Action, PinnServiceProfile, Feature


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


class ChartfieldForm(forms.Form):
    occ = forms.CharField(label='OCC', max_length=6)
    mrc = forms.CharField(label='MRS', max_length=6)
    local = forms.CharField(label='Local', max_length=6)
    longdistance = forms.CharField(label='Long Distance', max_length=6)

class ReviewForm(forms.Form):
    comments = forms.CharField(label='Additional Comments', max_length=100)
    review = forms.BooleanField(label='Accept Terms')

class NewLocationForm(forms.Form):
    label = 'Location Form'
    campuses= [
    ('A', 'Ann Arbor'),
    ('F', 'Flint'),
    ('D', 'Dearborn'),
    ]
    
    Campus = forms.ChoiceField(choices=campuses)
    building = forms.CharField(label='Building', max_length=100)
    floor = forms.CharField(label='Floor', max_length=100)
    room = forms.CharField(label='Room', max_length=100)
    jack = forms.BooleanField(label='Is there a Jack at the new location?')
    conduit = forms.BooleanField(label='Is there a Conduit at the new location?')


class EquipmentForm(forms.Form):
    equipment = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(), 
        widget=forms.RadioSelect,
    )


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