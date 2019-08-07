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

@permission_required('oscauth.can_report', raise_exception=True)
def get_inventory(request):
    depts = AuthUserDept.objects.filter(user=request.user.id).order_by('dept').exclude(dept='All').values().distinct('dept')
    departments = []
    for dept in depts:
        departments.append(dept['dept'])
    dates = UmOscBillCycleV.objects.values_list('billing_date', flat = True).order_by('billing_date').distinct().reverse()

    names = []
    name_query = list(d.dept_name for d in UmOscDeptProfileV.objects.filter(deptid__in=departments).order_by('deptid'))
    for i in range(0, len(departments)):
    	name = {
    		'deptid': departments[i],
    		'name': name_query[i]
    	}
    	names.append(name)

    template = loader.get_template('inventory.html')
    objects = UmOscReptInvlocV.objects
    context = {
        'title': 'Inventory and Location Report',
        'depts': names,
        'dates': dates,
    }
    return HttpResponse(template.render(context,request))
    
@permission_required('oscauth.can_report', raise_exception=True)
def make_report(request):
    data = []
    total_charge = 0
    formated_data = []
    cost_table = []
    
    total =  request.POST.get('dept_id') # 456000 #
    array = total.split('-')
    dept_id = array[0]
    dept_name = array[1]
   
    bill_period =  request.POST.get('bill_period') #  'May 20, 2018' #
    date = bill_period.replace('.', '')
    date = date.replace(',', '')
    date = date.split(' ')
    date[0] = date[0][0:3]
    date = date[0] + ' ' + date[1] + ' ' + date[2]
    date = datetime.strptime(date, '%b %d %Y')
    date = str(date.year) + '-' + str(date.month) + '-' + str(date.day)
    
    months_list = UmOscBillCycleV.objects.values_list('billing_date', flat = True).order_by('billing_date').distinct().reverse()
    curr_period = months_list[0]
    filter_months = (months_list[5], months_list[11])

    data = UmOscReptInvlocV.objects.filter(billing_date__exact = date, org__exact = dept_id).order_by('fund','org', 'program', 'subclass', 'project_grant', 'user_defined_id', 'rptorder', 'item_code').values().distinct()
    
    buildings = data.exclude(building = None).order_by('building').values_list('building', flat = True).distinct()
    user_types = data.exclude(cd_descr = None).order_by('cd_descr').values_list("cd_descr", flat= True).distinct()
    chartfields = data.exclude(chartfield = None).order_by('chartfield').values_list('chartfield',flat = True).distinct()
    total_charge = 0

    location_filter = ''
    type_filter = ''
    cf_filter = ''
    date_filter = ''
    if request.POST.get('location')!= '' and request.POST.get('location')!= None:
        location_filter = request.POST.get('location')
        data = data.filter(building__exact = location_filter).order_by('fund','org', 'program', 'subclass', 'project_grant', 'user_defined_id', 'rptorder', 'item_code').values().distinct()
    if request.POST.get('type')!= ''and  request.POST.get('type')!= None:
        type_filter = request.POST.get('type')
        data = data.filter(cd_descr__exact = type_filter).order_by('fund','org', 'program', 'subclass', 'project_grant', 'user_defined_id', 'rptorder', 'item_code').values().distinct()
    if request.POST.get('cf')!= '' and  request.POST.get('cf')!= None:
        cf_filter = request.POST.get('cf')
        data = data.filter(chartfield__exact = cf_filter).order_by('fund','org', 'program', 'subclass', 'project_grant', 'user_defined_id', 'rptorder', 'item_code').values().distinct()
    if request.POST.get('date')!= '' and  request.POST.get('date')!= None:
        date_filter = request.POST.get('date')
        if date_filter == '6-12':
            date_filter = "Greater than 6 months and less than 12 months"
            data = data.filter(last_call_date__lte = months_list[5], last_call_date__gte = months_list[11]).order_by('fund','org', 'program', 'subclass', 'project_grant', 'user_defined_id', 'rptorder', 'item_code').values().distinct()
        else:
            date_filter = "Greater than 12 months"
            data = data.filter(last_call_date__lte = months_list[11]).order_by('fund','org', 'program', 'subclass', 'project_grant', 'user_defined_id', 'rptorder', 'item_code').values().distinct()
      
    if list(data) != []:
        formated_data, cost_table = format_data(data,request)
    first = datetime.strptime(date,'%Y-%m-%d').date() == curr_period


    template = loader.get_template('inventory-report.html')
    context = {
        'title': 'Inventory and Location Report',
        'dept_id': dept_id,
        'dept_name': dept_name,
        'bill_period': bill_period,
        'data': list(data),
        'total_charge': total_charge,
        'formated_data': formated_data,
        'cost_table': list(cost_table),
        'buildings': list(buildings),
        'user_types': list(user_types),
        'chartfields': list(chartfields),
        'location_filter': location_filter,
        'type_filter': type_filter,
        'cf_filter': cf_filter,
        'date_filter': date_filter,
        'first': first,
        'months_list': filter_months,

    }
    return HttpResponse(template.render(context,request))


def format_data(data,request):
    whole_table = []
    
    chartfield_cost = 0
    cost_table = []

    current_classification = data.order_by('fund','org', 'program', 'subclass', 'project_grant').values_list('fund','org', 'program', 'subclass', 'project_grant').distinct()[0]
    current_table = []
    same_phone = []
    current_number = data.order_by('fund','org', 'program', 'subclass', 'project_grant').values_list('id').distinct()[0][0]
    for point in data:
        classification = (point['fund'],point['org'],point['program'],point['subclass'],point['project_grant'])
        number = point['id']
        if number!=current_number:
            if point == data[0]:
                same_phone.append(point)
                continue
            current_table.append(same_phone)
            same_phone = []
            current_number = number
        
        if classification != current_classification:
            whole_table.append(current_table)
            current_table = []
            current_classification = classification
            cost_table.append(chartfield_cost)
            chartfield_cost = 0

        same_phone.append(point)
        if point['charge_amount']!=None:
            chartfield_cost += point['charge_amount']
    if same_phone != []:
        current_table.append(same_phone)
        whole_table.append(current_table)
        cost_table.append(chartfield_cost)
    
    return whole_table, cost_table