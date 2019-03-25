from django import forms
from django.forms import ModelForm
from .models import Product, Service, Action, PinnServiceProfile, Feature


class WorkflowForm(forms.Form):
    service = forms.ModelChoiceField(Service.objects.all(), to_field_name="name")
    action = forms.ModelChoiceField(Action.objects.all(), to_field_name="name")
    
    class Meta:
        model = Service
        fields = ('name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['action'].queryset = Action.objects.none()

class FeaturesForm(forms.Form):
    features = forms.ModelMultipleChoiceField(
        queryset=Feature.objects.all(), 
        widget=forms.CheckboxSelectMultiple,
    )
    

class PhoneForm(forms.Form):
    phones = PinnServiceProfile.objects.filter(deptid='481054')
    phone_number = forms.ModelChoiceField(phones)
    phone_number = forms.ModelChoiceField(phones)
    #content = forms.Textarea('or search by uniqname')   
    uniqname = forms.CharField(label='Uniqname', max_length=8)

class ReviewForm(forms.Form):
    review = forms.CharField(label='Review', max_length=100)
    review = forms.BooleanField(label='Accept Terms')

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
    
    Campus = forms.ChoiceField(choices=campuses)
    building = forms.CharField(label='Building', max_length=100)
    floor = forms.CharField(label='Floor', max_length=100)
    room = forms.CharField(label='Room', max_length=100)


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description']