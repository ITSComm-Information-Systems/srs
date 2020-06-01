from django.template import Library
from django.core import serializers
import json

from django.http import JsonResponse
from django.forms.models import model_to_dict

register = Library()

@register.filter
def jsonify(queryset):
	queryset = model_to_dict(queryset)
	return json.dumps(queryset)
