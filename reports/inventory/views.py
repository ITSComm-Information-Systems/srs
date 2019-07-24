import warnings

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.template import loader
from django import template
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
from oscauth.models import AuthUserDept, Grantor, Role

# from .models import AuthUserDept
# from .models import Role, Group, User
# from .forms import UserSuForm, AddUserForm
# from .utils import su_login_callback, custom_login_action, upsert_user
from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV, UmOscReptInvlocV, UmOscBillCycleV
from oscauth.forms import *
from datetime import datetime

def get_inventory(request):
    depts = AuthUserDept.objects.filter(user=request.user.id).order_by('dept').exclude(dept='All').values().distinct()
    departments = []
    for dept in depts:
        departments.append(dept['dept'])
    dates = UmOscBillCycleV.objects.values_list('billing_date', flat = True).order_by('billing_date').distinct().reverse()

    dept_id = ''
    bill_period = ''
    submit = False
    date = ''
    data = []
    total_charge = 0
    formated_data = []
    cost_table = []

    if request.POST.get('dept_id') is None:
        dept_id = depts[0]
    else:
        dept_id = request.POST.get('dept_id')
    if request.POST.get('bill_period') is None:
        bill_period = ''
    else:
        bill_period = request.POST.get('bill_period')
        date = bill_period.replace('.', '')
        date = date.replace(',', '')
        date = date.split(' ')
        date[0] = date[0][0:3]
        date = date[0] + ' ' + date[1] + ' ' + date[2]
        date = datetime.strptime(date, '%b %d %Y')
        date = str(date.year) + '-' + str(date.month) + '-' + str(date.day)
        submit = True
    if submit == True:
        data = UmOscReptInvlocV.objects.filter(billing_date__exact = date, org__exact = '456000').order_by('fund','org', 'program', 'subclass', 'project_grant', 'user_defined_id', 'rptorder', 'item_code').values().distinct()
        
        total_charge = 0

        for point in data:
            if point['charge_amount'] != None:
                total_charge += point['charge_amount']

        formated_data, cost_table = format_data(data,request)
    # order by project grant, then by user id, which weill most likely have 2 entries for each
    # because of the rpt order A/B,






    template = loader.get_template('inventory.html')
    objects = UmOscReptInvlocV.objects
    context = {
        'title': 'Inventory and Location Report',
        'depts': departments,
        'dates': dates,
        'dept_id': dept_id,
        'bill_period': bill_period,
        'data': list(data),
        'submit': submit,
        'total_charge': total_charge,
        'formated_data': formated_data,
        'cost_table': list(cost_table),
    }
    return HttpResponse(template.render(context,request))

def format_data(data,request):
    whole_table = []
    current_classification = data.order_by('fund','org', 'program', 'subclass', 'project_grant').values_list('fund','org', 'program', 'subclass', 'project_grant').distinct()[0]
    current_table = []
    chartfield_cost = 0
    cost_table = []
    same_phone = []
    for point in data:
        classification = (point['fund'],point['org'],point['program'],point['subclass'],point['project_grant'])
        if classification != current_classification:
            whole_table.append(current_table)
            current_table = []
            current_classification = classification
            cost_table.append(chartfield_cost)
            chartfield_cost = 0

        current_table.append(point)
        if point['charge_amount']!=None:
            chartfield_cost += point['charge_amount']

    
    return whole_table, cost_table

# def format_data(data,request):
#     whole_table = []
    
#     chartfield_cost = 0
#     cost_table = []

#     current_classification = data.order_by('fund','org', 'program', 'subclass', 'project_grant').values_list('fund','org', 'program', 'subclass', 'project_grant').distinct()[0]
#     current_table = []
 
#     same_phone = []
#     current_number = data.order_by('fund','org', 'program', 'subclass', 'project_grant').values_list('last_name').distinct()[0]
    
#     for point in data:
#         classification = (point['fund'],point['org'],point['program'],point['subclass'],point['project_grant'])
#         number = point['last_name']

#         if number == current_number:
#             same_phone.append(point)
#         else:
#             current_table.append(same_phone)
#             same_phone = []
        
#         if classification != current_classification:
#             whole_table.append(current_table)
#             current_table = []
#             current_classification = classification
#             cost_table.append(chartfield_cost)
#             chartfield_cost = 0

        

#         current_table.append(point)
#         if point['charge_amount']!=None:
#             chartfield_cost += point['charge_amount']

    
    return whole_table, cost_table









register = template.Library()
@register.filter
def index(list, i):
    return list[int(i)]