import warnings

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404
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
from project.pinnmodels import UmOscLocationsInUseV

def get_voip(request):
    template = loader.get_template('voip.html')
    phone_number = request.POST.get('number', None)
    current = UmOscLocationsInUseV.objects.filter(service_number__exact = phone_number).order_by('room').values_list().distinct()
    locations = UmOscLocationsInUseV.objects.values_list('campuscd', 'campus_desc').order_by('campus_desc').distinct()
    context = {
        'title': 'VOIP Location Change',
        'phone_number': phone_number,
        'current': current,
        'locations': locations,
    }
    return HttpResponse(template.render(context,request))

