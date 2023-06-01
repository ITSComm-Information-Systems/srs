from django.forms import ModelForm
from django import forms
from .models import Favorite, Estimate, Material, Project, Labor, Technician, LaborGroup, PreDefinedNote

# Let's hang on to these, they rarely change
LABOR_GROUP_CHOICES = [('','----')] + list(LaborGroup.objects.all().values_list('id', 'name'))
NOTE_TYPE_CHOICES = list(PreDefinedNote.objects.all().values_list('id', 'subject'))
 

class FavoriteForm(ModelForm): 

    class Meta:
        model = Favorite
        exclude = ['id']


class EstimateForm(ModelForm): 

    class Meta:
        model = Estimate
        fields = ['label', 'status', 'folder', 'contingency_amount','contingency_percentage','assigned_engineer','engineer_status']

    def __init__(self, *args, **kwargs):
        super(EstimateForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['assigned_engineer'].queryset = Technician.objects.filter(active=Technician.ACTIVE).order_by('labor_name_display')

        self.fields['contingency_amount'].required = False
        self.fields['contingency_percentage'].required = False
        self.fields['folder'].required = False
        self.note_type_list = NOTE_TYPE_CHOICES

class LaborForm(ModelForm): 
    group = forms.ChoiceField(choices=LABOR_GROUP_CHOICES)

    class Meta:
        model = Labor
        exclude = ['id']
 
    def __init__(self, *args, **kwargs):
        super(LaborForm, self).__init__(*args, **kwargs)

        if self.instance.hours:
             self.extended_cost = self.instance.extended_cost


class MaterialLocationForm(ModelForm):  

    class Meta:
        model = Material
        exclude = ['id']

    def __init__(self, *args, **kwargs):
        super(MaterialLocationForm, self).__init__(*args, **kwargs)

        #self.extended_price = 0
        if self.instance.quantity:
            self.extended_price = self.instance.extended_price
        else:
            self.extended_price = 0

class MaterialForm(ModelForm):  

    class Meta:
        model = Material
        exclude = ['id']
        widgets = {
            'estimated_receive_date': forms.DateInput(attrs={'type': 'date'}),
            'order_date': forms.DateInput(attrs={'type': 'date'})
        }
        

class ProjectForm(ModelForm):
    prefix = 'project'
    
    class Meta:
        model = Project
        fields = ['netops_engineer','assigned_date','due_date','completed_date','status']
        labels = {
        "netops_engineer":  "UMNet Engineer",
        }
        widgets = {
            'assigned_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'completed_date': forms.DateInput(attrs={'type': 'date'})
        }
        

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['netops_engineer'].queryset = Technician.objects.filter(active=Technician.ACTIVE, wo_group_code = 'Network Operation').order_by('labor_name_display')