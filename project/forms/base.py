from django import forms
from django.core.exceptions import ValidationError


OPTION_LIST = ((1, 'One'), (2, 'Two'), (3, 'Three'))

class SampleForm(forms.Form):

    name = forms.CharField(help_text='Enter a descriptive name.')
    recipients = forms.CharField(label='Recipient List', help_text='Enter all recipients.')
    option = forms.ChoiceField(choices=OPTION_LIST)
    units = forms.ChoiceField(choices=OPTION_LIST, widget=forms.RadioSelect)
    add_ons = forms.ChoiceField(choices=OPTION_LIST, widget=forms.CheckboxSelectMultiple, required=False)

    def clean_recipients(self):  # From Django Docs:
        data = self.cleaned_data["recipients"]
        if "fred@example.com" not in data:
            raise ValidationError("You have forgotten about Fred!")

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return data
    