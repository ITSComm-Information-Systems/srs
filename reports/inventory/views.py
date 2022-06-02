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
from oscauth.models import AuthUserDept, Grantor, Role, AuthUserDeptV
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Case, When, Value, IntegerField

from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV, UmOscReptInvlocV, UmOscBillCycleV
from oscauth.forms import *
from datetime import datetime

from pages.models import Page


# Load selection page
@permission_required('oscauth.can_report', raise_exception=True)
def get_inventory(request):
    template = loader.get_template('inventory.html')

    # Find all departments user has reporting access to
    names = AuthUserDept.get_report_departments(request)

    # Find available billing dates
    dates = UmOscBillCycleV.objects.values_list('billing_date', flat = True).order_by('billing_date').distinct().reverse()

    # Get instructions
    instructions = Page.objects.get(permalink='/ial')
    
    edit_dept = 'None'
    edit_date = 'None'
    if request.method =='POST':
        # Get information from previous page
        edit_dept = request.POST.get('edit_dept')
        edit_date = request.POST.get('edit_date')

    context = {
        'title': 'Inventory & Location Report',
        'instructions': instructions,
        'depts': names,
        'dates': dates,

        'edit_dept': edit_dept,
        'edit_date': edit_date
    }
    return HttpResponse(template.render(context,request))
    

# Build report
@permission_required('oscauth.can_report', raise_exception=True)
def make_report(request):
    # Initialize variables
    data = []
    total_charge = 0
    formated_data = []
    cost_table = []
    
    # Get user-selected department ID and name
    total =  request.POST.get('dept_id')

    if total is None:
        return HttpResponseRedirect('/reports/inventory')

    array = total.split('-')
    dept_id = array[0]
    dept_name = array[1]

    # Find dept manager and uniqname
    dept_info = UmOscDeptProfileV.objects.filter(deptid=dept_id)[0]
    dept_mgr = dept_info.dept_mgr
    dept_mgr_uniq = dept_info.dept_mgr_uniqname
      
    # Get user-selected billing period & format appropriately
    bill_period = request.POST.get('bill_period')
    date = bill_period.replace('.', '')
    date = date.replace(',', '')
    date = date.split(' ')
    date[0] = date[0][0:3]
    date = date[0] + ' ' + date[1] + ' ' + date[2]
    date = datetime.strptime(date, '%b %d %Y')
    date = str(date.year) + '-' + str(date.month) + '-' + str(date.day)

    # Find data to populate the month filter
    months_list = UmOscBillCycleV.objects.values_list('billing_date', flat = True).order_by('billing_date').distinct().reverse()
    curr_period = months_list[0]
    filter_months = (months_list[5], months_list[11])

    # Pull data using selected department ID and billing date
    data = UmOscReptInvlocV.objects.filter(billing_date__exact = date, org__exact = dept_id).order_by('chartfield', 'user_defined_id', 'rptorder', 'item_code').values().distinct()
    
    # Find data to populate filter
    buildings = data.exclude(building = None).order_by('building').values_list('building', flat = True).distinct()
    user_types = data.exclude(cd_descr = None).order_by('cd_descr').values_list("cd_descr", flat= True).distinct()
    chartfields = data.exclude(chartfield = None).order_by('chartfield').values_list('chartfield',flat = True).distinct()
    total_charge = 0

    # # If they filter by date
    # if request.POST.get('date')!= '' and  request.POST.get('date')!= None:
    #     date_filter = request.POST.get('date')
    #     if date_filter == '6-12':
    #         date_filter = "Greater than 6 months and less than 12 months"
    #         data = data.filter(last_call_date__lte = months_list[5], last_call_date__gte = months_list[11]).order_by('chartfield', 'user_defined_id', 'rptorder', 'item_code').values().distinct()
    #     else:
    #         date_filter = "Greater than 12 months"
    #         data = data.filter(last_call_date__lte = months_list[11]).order_by('chartfield', 'user_defined_id', 'rptorder', 'item_code').values().distinct()
    data = data.annotate(lt_twelve = Case(When(last_call_date__gt=months_list[11], then=Value(1)), default=Value(0), output_field=IntegerField()),
                        gt_six = Case(When(last_call_date__lt=months_list[5], then=Value(1)), default=Value(0), output_field=IntegerField()))


    # Format the report data
    if list(data):
        formated_data, cost_table = format_data(data,request)
    first = datetime.strptime(date,'%Y-%m-%d').date() == curr_period


    template = loader.get_template('inventory-report.html')
    context = {
        'title': 'Inventory & Location Report',
        'dept_id': dept_id,
        'dept_name': dept_name,
        'dept_mgr': dept_mgr,
        'dept_mgr_uniq': dept_mgr_uniq,
        'bill_period': bill_period,
        'data': list(data),
        'data_length': len(data) < 1000,
        'total_charge': total_charge,
        'formated_data': formated_data,
        'cost_table': list(cost_table),
        'buildings': list(buildings),
        'user_types': list(user_types),
        'chartfields': list(chartfields),
        'first': first,
        'months_list': filter_months,

        'edit_dept': total
    }
    return HttpResponse(template.render(context,request))


def format_data(data, request):
    whole_table = []
    
    chartfield_cost = 0
    cost_table = []

    # Find first chartfield
    current_classification = data.values_list('chartfield').distinct()[0][0]
    
    # Build data structure
    current_table = []
    same_phone = []

    # Get ID of first entry of data set (filtered by selected department and date)
    current_number = data.values_list('user_defined_id').distinct()[0][0]

    # Loop through all report data
    for point in data:
        # Create chartfield-like object
        classification = point['chartfield']
        number = point['user_defined_id']

        # Current loop variable is different than the previous (current)
        if number != current_number:
            # If this is the first entry of the data set, add it to the current User ID list
            if point == data[0]:
                same_phone.append(point)
                continue
            current_table.append(same_phone)
            same_phone = []
            current_number = number

        
        # If new chartfield is reached, append previous chartfield's data to result table
        # and reset current chartfield
        if classification != current_classification:
            whole_table.append(current_table)
            current_table = []
            current_classification = classification
            cost_table.append(chartfield_cost)
            chartfield_cost = 0

        # Add user ID info to tables       
        same_phone.append(point)
        if point['charge_amount'] != None:
            chartfield_cost += point['charge_amount']

    # Add last data point if necessary        
    if same_phone:
        current_table.append(same_phone)
        whole_table.append(current_table)
        cost_table.append(chartfield_cost)
    
    return whole_table, cost_table

def get_depts(request):
    if request.user.has_perm('can_order_all'):
        query = UmOscDeptProfileV.objects.all().order_by('deptid')
        return list(query)
    else:
        query = AuthUserDeptV.objects.filter(user=request.user.id, codename='can_report').order_by('dept')
        full_depts = []
        for d in query:
            name = UmOscDeptProfileV.objects.filter(deptid=d.dept)[0].dept_name
            dept ={
                'deptid': d.dept,
                'dept_name': name
            }
            full_depts.append(dept)
        return full_depts

def filter(request):
    template = loader.get_template('inventory-report.html')
    context = {
        'title': 'Test!!!',
    }
    return HttpResponse(template.render(context,request))
