from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import get_user_model

from oscauth.models import AuthUserDept

from dal import autocomplete
from django_select2.forms import Select2MultipleWidget, Select2Widget, ModelSelect2Widget, ModelSelect2MultipleWidget

class DeptForm(forms.Form):
	deptids = forms.ChoiceField(label='Department ID', choices=[], widget=Select2Widget(attrs={'data-width': '15%'}))

	def __init__(self, depts=None, *args, **kwargs):
		super(DeptForm, self).__init__(*args, **kwargs)
		if depts:
			DEPT_CHOICES = []
			DEPT_CHOICES.append(tuple(['', 'Select a department']))
			for d in depts:
				DEPT_CHOICES.append(tuple([d, d]))
			self.fields['deptids'].choices = DEPT_CHOICES
