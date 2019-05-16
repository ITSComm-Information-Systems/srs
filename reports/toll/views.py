import warnings
from datetime import datetime

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.template import loader

from django.contrib.auth.models import User
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
from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV
from oscauth.forms import *

def get_tolls(request):
    template = loader.get_template('tolls.html')
    date_list = get_periods(request)
    context = {
        'date_list': date_list,
    }
    return HttpResponse(template.render(context,request))

def get_periods(request):
    date_list = []
    for x in range(13):
        now = datetime.now()
        month = now.month-x if now.month-x>=1 else 12-(x-now.month)
        year = now.year -1 if now.month-x<1 else now.year
        months = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()[month-1]      
        date_list.append([months, year])

    return date_list