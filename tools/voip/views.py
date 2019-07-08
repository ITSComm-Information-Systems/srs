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
    

def new_building(request):
    name = request.GET.get('buildingName',None)
    code = request.GET.get('buildingID',None)
    data = {
        'name': name,
        'code': code,
    }
    return JsonResponse(data)

def new_floor(request):
    floor = request.GET.get('buildingFloor',None)
    data = {
        'floor': floor,
    }
    return JsonResponse(data)

def new_room(request):
    room = request.GET.get('buildingRoom',None)
    data = {
        'room': room,
    }
    return JsonResponse(data)
    
def new_jack(request):
    jack = request.GET.get('buildingJack',None)
    data = {
        'jack': jack,
    }
    return JsonResponse(data)
    
def confirm(request):
    template = loader.get_template('confirm.html')
    unique_name = 'TEST TEST TEST'

    phone_number = request.GET.get('holder',None)
    old_jack = request.GET.get('jacks',None)
    selected = UmOscLocationsInUseV.objects.filter(service_number__exact = phone_number, jack__exact = old_jack).order_by('room').values_list().distinct()
    
    new_name = request.GET.get('buildingName',None)
    new_code = request.GET.get('buildingID',None)
    new_floor = request.GET.get('buildingFloor',None)
    new_jack = request.GET.get('buildingJack',None)

    context = {
        'title': 'Voip Confirmation Page',
        'phone_number': phone_number,
        'old_jack': old_jack,
        'selected': selected,

    }
    return HttpResponse(template.render(context,request))
    