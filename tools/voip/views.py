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
    if phone_number:
        phone_number = phone_number.replace('-','')
    current = UmOscLocationsInUseV.objects.filter(service_number__exact = phone_number).order_by('room').values().distinct()
    building_list = UmOscAvailableLocsV.objects.values_list('building_id', 'building_name', 'campus_desc').distinct()
    selected = ''
    choice = ''
    if phone_number!= None:
        submit = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        choice = request.GET.get('jacks',None)
        selected = UmOscLocationsInUseV.objects.filter(service_number__exact = phone_number, jack__exact = choice).order_by('room').values().distinct()
        
    context = {
        'title': 'VoIP Location Change',
        'phone_number': phone_number,
        'current': list(current),
        'building_list': list(building_list),
        'submit': submit,
        'selected': list(selected),
        'choice':choice,
        

    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
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
    code = request.GET.get('buildingID', None)
    rooms = UmOscAvailableLocsV.objects.filter(building_id__exact = code, floor__exact = floor).order_by('room').values_list('room').distinct()
    data = {
        'floor': floor,
        'code': code,
        'rooms': list(rooms),
    }
    return JsonResponse(data)

def new_room(request):
    room = request.GET.get('buildingRoom',None)
    floor = request.GET.get('buildingFloor',None)
    code = request.GET.get('buildingID', None)
    jacks = UmOscAvailableLocsV.objects.filter(building_id__exact = code, floor__exact = floor, room__exact = room).order_by('jack').values_list('jack').distinct()
    
    data = {
        'room': room,
        'jacks': list(jacks),
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

    phone_number = request.GET.get('phone-num',None)
    current_jack = request.GET.get('jacks',None)
    selected = UmOscLocationsInUseV.objects.filter(service_number__exact = phone_number, jack__exact = current_jack).order_by('room').values().distinct()
    
    new_name = request.GET.get('buildingName',None)
    new_code = request.GET.get('buildingID',None)
    new_floor = request.GET.get('buildingFloor',None)
    new_room = request.GET.get('buildingRoom', None)
    new_jack = request.GET.get('buildingJack',None)
    new_location = UmOscAvailableLocsV.objects.filter(building_name__exact = new_name, building_id__exact = new_code, floor__exact = new_floor, room__exact = new_room).values_list().distinct()

    if new_jack != '%':
        new_location = new_location.filter(jack__exact = new_jack)

    p = UmOscVoipLocChangeInput(uniqname = unique_name, service_id = selected[0]['service_id'], service_number = phone_number, # service_subscrib_id = selected[0]['service_subscrib_id'],
        old_campuscd = selected[0]['campuscd'], old_campus_desc = selected[0]['campus_desc'], old_location_id = selected[0]['location_id'], 
        old_path_id = selected[0]['path_id'], old_building_id = selected[0]['building_id'], old_building_name = selected[0]['building_name'], old_floor = selected[0]['floor'],
        old_floor_desc = None, old_room = selected[0]['room'], old_room_desc = None,
        old_jack = current_jack, service_id_at_new_loc = None, service_nbr_at_new_loc = None,
        service_type_at_new_loc = None, svc_status_at_new_loc = None, new_campuscd = new_location[0][0], new_campus_desc = new_location[0][1], new_location_id = new_location[0][6], 
        new_path_id = new_location[0][7], new_building_id = new_location[0][8], new_building_name = new_location[0][9], new_floor = new_location[0][10],
        new_floor_desc = None, new_room = new_location[0][12], new_room_desc = None,
        new_jack = new_jack, request_no = None, date_added = date.today(), date_processed = None, messages = None)
    
    p.save()

    curr = connections['pinnacle'].cursor()
    p_uniqname = unique_name
    p_datetime_added = date.today()
    curr.callproc('UM_VOIP_PROCEDURES_K.UM_MOVE_VOIP_SERVICE_P',[p_uniqname,p_datetime_added])
    curr.close()

    query = UmOscVoipLocChangeInput.objects.filter(service_number = phone_number, old_jack__exact = current_jack, uniqname__exact = p_uniqname, date_added__exact = p_datetime_added).values("messages").distinct()[0]["messages"]
    # query the table and recieve the message to display to the user

    context = {
        'title': 'VoIP Location Change Status',
        'phone_number': phone_number,
        'old_jack': current_jack,
        'selected': selected,
        'new_location': new_location,
        'query': query,

    }
    return HttpResponse(template.render(context,request))
    