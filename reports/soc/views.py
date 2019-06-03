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

# from .models import AuthUserDept
# from .models import Role, Group, User
# from .forms import UserSuForm, AddUserForm
# from .utils import su_login_callback, custom_login_action, upsert_user
from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV, UmOscDeptUnitsRept
from oscauth.forms import *
import datetime

def get_soc(request):
    template = loader.get_template('soc.html')
    depts = find_depts(request)
    groups = []
    query = UmOscDeptProfileV.objects.filter(deptid__in=depts).order_by('dept_grp').exclude(dept_grp='All')
    for q in query:
        groups.append(q.dept_grp)
    groups = list(dict.fromkeys(groups))
    fiscal = select_fiscal_year(request)
    calendar = select_calendar_year(request)
    months = select_month(request)

    vps = []
    vps = UmOscDeptUnitsRept.objects.filter(dept_grp__in = groups).order_by('dept_grp_vp_area').exclude(dept_grp='All').values_list('dept_grp_vp_area',flat =True).distinct()


    unit = ''
    grouping = ''
    display_type = request.POST.get("unitGroupingGroup",None)
    if display_type in ['1']:
        grouping = 'Department ID'
        unit = request.POST.get('department_id')
    elif display_type in ['2']:
        grouping = 'Department Group'
        unit = request.POST.get('department_group')
    elif display_type in ['3']:
        grouping = 'Department Group VP Area'
        unit = request.POST.get('department_vp')

    billing_period = ''
    dateRange = ''
    display_type = request.POST.get("dateRangeGroup",None)
    if display_type in ['1']:
        dateRange = 'Fiscal Year'
        billing_period = request.POST.get('FISCALYEAR')
    elif display_type in ['2']:
        dateRange = 'Calendar Year'
        billing_period = request.POST.get('CALENDARYEAR')
    elif display_type in ['3']:
        dateRange = 'Single Month'
        billing_period = request.POST.get('SINGLEMONTH')
        billing_period = billing_period + " " + request.POST.get('SINGLEYEAR')
    elif display_type in ['4']:
        dateRange = 'Month-to-Month'
        billing_period = request.POST.get('FIRSTMONTH')
        billing_period = billing_period + " " + request.POST.get('FIRSTYEAR') + " to "
        billing_period = billing_period + " " + request.POST.get('SECONDMONTH')
        billing_period = billing_period + " " + request.POST.get('SECONDYEAR')

    context = {
        'title': 'Summary of Charges',
        'depts': depts,
        'groups': groups,
        'fiscal':fiscal,
        'calendar':calendar,
        'months':months,
        'vps': vps,
        'grouping': grouping,
        'dateRange': dateRange,
        'unit': unit,
        'billing_period': billing_period,
    }
    return HttpResponse(template.render(context,request))


def find_depts(request):
 	depts = []

 	query = AuthUserDept.objects.filter(user=request.user.id).order_by('dept').exclude(dept='All').distinct('dept')

 	for dept in query:
 		if Group.objects.get(name=dept.group).name != 'Orderer':
 			depts.append(dept.dept)

 	return depts

def select_fiscal_year(request):
    query = UmOscDeptUnitsRept.objects.order_by('fiscal_yr').values_list('fiscal_yr',flat =True).distinct()
    return query.reverse()
    
def select_calendar_year(request):
    query = UmOscDeptUnitsRept.objects.order_by('calendar_yr').values_list('calendar_yr',flat =True).distinct()
    return query.reverse()

def select_month(request):
    query = UmOscDeptUnitsRept.objects.order_by('month').values_list('month',flat =True).distinct()
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
 	 		  'August', 'September', 'October', 'November', 'December']
    return months #,query

# def find_groups(request):
#     groups = []

#     query = UmOscDeptProfileV.objects.filter(deptid_

#     for group in query:
#         groups.append(group)
#     return groups