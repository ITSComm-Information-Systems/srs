from django import forms
from django.forms import ModelForm
from .models import Product, Service, Action, Feature, FeatureCategory, Restriction
from project.pinnmodels import UmOSCBuildingV

class FeaturesForm(forms.Form):
    features = forms.ModelMultipleChoiceField(
        queryset=Feature.objects.all(), 
        widget=forms.CheckboxSelectMultiple(),
    )
    features = Feature.objects.all()
    list = FeatureCategory.objects.all()

    for cat in list:
        cat.type = ['STD','OPT','SC','VM']
        cat.type[0] = features.filter(category=cat).filter(type='STD')
        cat.type[0].label = 'Standard'
        cat.type[1] = features.filter(category=cat).filter(type='OPT')
        cat.type[1].label = 'Optional'
        cat.type[2] = features.filter(category=cat).filter(type='SPD')
        cat.type[2].label = 'Speed Call'
        cat.type[3] = features.filter(category=cat).filter(type='VM')
        cat.type[3].label = 'Voicemail'

    template = 'order/features.html'

    class Meta:
        model = Feature
        fields = ('name', 'description',) 


class RestrictionsForm(forms.Form):
    res = Restriction.objects.all()
    list = FeatureCategory.objects.all()

    for cat in list:
        cat.res = res.filter(category=cat)

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


class NewLocationForm(forms.Form):
    building_list = UmOSCBuildingV.objects.all()
    building = forms.CharField(label='Building', max_length=100)
    floor = forms.CharField(label='Floor', max_length=100)
    room = forms.CharField(label='Room', max_length=100)

    template = 'order/location.html'


class EquipmentForm(forms.Form):
    cat = ['Basic','VOIP']
    cat[0] = Product.objects.all().filter(category=1).order_by('display_seq_no')
    cat[0].id = 'basic'
    cat[1] = Product.objects.all().filter(category=2).order_by('display_seq_no') 
    cat[1].id = 'voip'
    template = 'order/products.html'


class PhoneLocationForm(forms.Form):
    phone_number = forms.CharField(label='Current Phone Number')
    building = forms.CharField(label='Building', max_length=100)
    floor = forms.CharField(label='Floor', max_length=100)
    room = forms.CharField(label='Room', max_length=100)
    jack = forms.CharField(max_length=100)
    template = 'order/phone_location.html'
