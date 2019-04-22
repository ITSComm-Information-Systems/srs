from django import forms

class YesNoInput(forms.RadioSelect):
    template_name = 'order/yesno.html'