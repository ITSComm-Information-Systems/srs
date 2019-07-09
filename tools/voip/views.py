import warnings

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404, JsonResponse
from django.template import loader
from django.conf import settings
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
from django.db.models import indexes, Max
from django.db import connections
from django import db
from project.pinnmodels import UmOscLocationsInUseV, UmOSCCampusBuildingV,  UmOscAvailableLocsV, UmOSCBuildingV, UmOscVoipLocChangeInput
import os
import cx_Oracle
from datetime import date

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
    unique_name = request.user.username

    phone_number = request.GET.get('holder',None)
    current_jack = request.GET.get('jacks',None)
    selected = UmOscLocationsInUseV.objects.filter(service_number__exact = phone_number, jack__exact = current_jack).order_by('room').values_list().distinct()
    
    new_name = request.GET.get('buildingName',None)
    new_code = request.GET.get('buildingCode',None)
    new_floor = request.GET.get('buildingFloor',None)
    new_room = request.GET.get('buildingRoom', None)
    new_jack = request.GET.get('buildingJack',None)
    new_location = UmOscAvailableLocsV.objects.filter(building_name__exact = new_name, building_id__exact = new_code, floor__exact = new_floor, room__exact = new_room, jack__exact = new_jack).values_list().distinct()

    p = UmOscVoipLocChangeInput(uniqname = 'dyangz', service_id = selected[0][5], service_number = phone_number,
        old_campuscd = selected[0][0], old_campus_desc = selected[0][1], old_location_id = selected[0][6], 
        old_path_id = selected[0][7], old_building_id = selected[0][8], old_building_name = selected[0][9], old_floor = selected[0][10],
        old_floor_desc = None, old_room = selected[0][12], old_room_desc = None,
        old_jack = current_jack, service_id_at_new_loc = None, service_nbr_at_new_loc = None,
        service_type_at_new_loc = None, svc_status_at_new_loc = None, new_campuscd = new_location[0][0], new_campus_desc = new_location[0][1], new_location_id = new_location[0][6], 
        new_path_id = new_location[0][7], new_building_id = new_location[0][8], new_building_name = new_location[0][9], new_floor = new_location[0][10],
        new_floor_desc = None, new_room = new_location[0][12], new_room_desc = None,
        new_jack = new_jack, request_no = None, date_added = date.today(), date_processed = None, messages = None)
    
    p.save()

    curr = connections['pinnacle'].cursor()
    p_uniqname = 'dyangz'
    p_datetime_added = date.today()
    curr.callproc('UM_VOIP_PROCEDURES_K.UM_MOVE_VOIP_SERVICE_P',[p_uniqname,p_datetime_added])
    curr.close()


    context = {
        'title': 'Voip Confirmation Page',
        'phone_number': phone_number,
        'old_jack': current_jack,
        'selected': selected,
        'new_location': new_location,

    }
    return HttpResponse(template.render(context,request))
    