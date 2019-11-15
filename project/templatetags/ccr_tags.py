from django.template import Library
from django.core import serializers
import json

from django.http import JsonResponse
from django.forms.models import model_to_dict

register = Library()

# @register.filter
# def jsonify(queryset):
# 	return json.dumps(queryset
#     #return serializers.serialize('json', queryset)

@register.filter
def jsonify(queryset):
	return model_to_dict(queryset)