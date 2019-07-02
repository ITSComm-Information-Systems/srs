import warnings

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404, JsonResponse
from django.template import loader

from django.contrib.auth.models import User, Group
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login, authenticate, user_logged_in
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_http_methods
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django import forms

from ldap3 import Server, Connection, ALL
from oscauth.models import AuthUserDept, Grantor, Role
from django.db.models import indexes
from project.pinnmodels import UmOscLocationsInUseV, UmOSCCampusBuildingV,  UmOscAvailableLocsV, UmOSCBuildingV

def get_voip(request):
    submit = False
    template = loader.get_template('voip.html')
    phone_number = request.GET.get('number', None)
    current = UmOscLocationsInUseV.objects.filter(service_number__exact = phone_number).order_by('room').values_list().distinct()
    building_list = UmOscAvailableLocsV.objects.values_list('building_id', 'building_name').distinct()
    selected = ''
    choice = ''
    if phone_number!= None:
        submit = True
    if request.is_ajax():
        choice = request.GET.get('jacks',None)
        selected = UmOscLocationsInUseV.objects.filter(service_number__exact = phone_number, jack__exact = choice).order_by('room').values_list().distinct()
        phone_number = '123489y128943'
    context = {
        'title': 'VOIP Location Change',
        'phone_number': phone_number,
        'current': list(current),
        'building_list': list(building_list),
        'submit': submit,
        'selected': list(selected),
        'choice':choice,
        

    }
    if request.is_ajax():
        return JsonResponse(context)
    return HttpResponse(template.render(context,request))
    #return JsonResponse(context)
    
def get_jack(request): # need to get this json working then we should be good
    phone_number = request.GET.get('number', None)
    choice = request.GET.get('jacks',None)
    selected = UmOscLocationsInUseV.objects.filter(jack__exact = choice).order_by('room').values_list().distinct()
    template = loader.get_template('voip.html')
    data = {
        'selected': selected,
        'choice':choice,

    }
    return JsonResponse(data)