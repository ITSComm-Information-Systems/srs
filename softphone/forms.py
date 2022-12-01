import datetime
from django import forms
from .models import Category, Selection
from project.forms.fields import Uniqname
from project.models import Choice

unselected = (None,'---',)

migrate_choices = list(Choice.objects.filter(parent__code='SOFTPHONE_MIGRATE').values_list('code','label').order_by('sequence'))
migrate_choices.insert(0, unselected)
yn_choices = [unselected ,(True,'Yes',), (False, 'No',)]

uniqname_choices = Selection.UNIQNAME_CHOICES
uniqname_choices.insert(0, unselected)

add_uniqname_choices = Selection.ADD_UNIQNAME_CHOICES
add_uniqname_choices.insert(0, unselected)

class SelectionForm(forms.ModelForm):  

    REQUIRED = 'This field is required.'

    subscriber = forms.CharField(widget=forms.HiddenInput())
    uniqname = Uniqname(required=False)
    location_correct = forms.ChoiceField(choices=yn_choices, required=False)
    migrate = forms.ChoiceField(choices=migrate_choices)
    other_category = forms.CharField(required=False)
    notes = forms.CharField(widget=forms.Textarea(), max_length=200, required=False)

    class Meta:
        model = Selection
        fields = ['subscriber', 'category', 'other_category', 'uniqname', 'uniqname_correct', 'migrate', 'notes', 'location_correct']
        #exclude = ['id','update_date','updated_by']
        

    def __init__(self, *args, **kwargs):
        super(SelectionForm, self).__init__(*args, **kwargs)

        self.fields['uniqname_correct'].required = False
        self.fields['category'].required = False

        self.fields['location_correct'].widget.attrs['class'] = 'location-correct'
        self.fields['uniqname_correct'].widget.attrs['class'] = 'verify-uniqname'
        self.fields['category'].widget.attrs['class'] = 'phone-category'
        self.fields['migrate'].widget.attrs['class'] = 'convert-softphone'

        if hasattr(self, 'initial'):
            if self.initial.get('user') == '':
                self.fields['uniqname_correct'].choices = add_uniqname_choices

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("migrate") == 'CANCEL':  
            self.cleaned_data.pop('category')
        else:
            if cleaned_data.get("uniqname_correct") == '':
                self.add_error('uniqname_correct', self.REQUIRED)

            if cleaned_data.get("category") == None:
                self.add_error('category', self.REQUIRED)

            if cleaned_data.get("location_correct"):
                if cleaned_data.get("migrate") in ('YES_SET','NOT_YET'):  
                    if cleaned_data.get("location_correct") == '':
                        self.add_error('location_correct', self.REQUIRED)

        if cleaned_data.get("uniqname_correct") == 'CHANGE':
            if cleaned_data.get("uniqname") == '':
                self.add_error('uniqname', self.REQUIRED)

        try:
            cat = getattr(cleaned_data.get('category'),'id')
        except:
            cat = 0

        if cat == Category.OTHER:
            if cleaned_data.get('other_category') == '':
                self.add_error('other_category', self.REQUIRED)

        if cat == Category.CONFERENCE_ROOM:
            if cleaned_data.get('notes') == '':
                self.add_error('notes', self.REQUIRED)

        for field in self.fields:
            if self.has_error(field):
                self.fields[field].widget.attrs['class'] = self.fields[field].widget.attrs.get('class','') + ' is-invalid'


    def save(self, username, *args, **kwargs):
        obj = super(SelectionForm, self).save(*args, **kwargs)

        for key, value in self.initial.items():
            if key not in self.fields:
                setattr(obj, key, value )

        if not obj.uniqname and self.initial['user']:
            obj.uniqname = self.initial['user']

        obj.update_date = datetime.datetime.now()
        obj.updated_by = username
        obj.save()

class OptOutForm(forms.Form):
    subscriber = forms.CharField(widget=forms.HiddenInput())
    pause_until = forms.CharField(required=False)
    comment = forms.CharField(required=False)

class LocationForm(forms.Form):
    subscriber = forms.CharField(widget=forms.HiddenInput())
    update = forms.BooleanField()
    building = forms.CharField()
    floor = forms.CharField()
    room = forms.CharField()