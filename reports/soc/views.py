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

from django.db.models import Value
from django.db.models.functions import Concat

# from .models import AuthUserDept
# from .models import Role, Group, User
# from .forms import UserSuForm, AddUserForm
# from .utils import su_login_callback, custom_login_action, upsert_user
from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV, UmOscDeptUnitsReptV
from oscauth.forms import *
import datetime


@permission_required('oscauth.can_report', raise_exception=True)
def get_soc(request):
    template = loader.get_template('soc.html')
    depts = find_depts(request)
    groups = UmOscDeptUnitsReptV.objects.filter(deptid__in=depts).order_by('dept_grp').values_list('dept_grp',flat = True).distinct()
    groups_descr = UmOscDeptUnitsReptV.objects.order_by('dept_grp_descr').values_list('dept_grp_descr',flat = True).distinct()
    # for i in range(255):
    #     valid = UmOscDeptUnitsReptV.objects.filter(dept_grp_descr__exact = groups_descr[i]).order_by('fiscal_yr').values_list('fiscal_yr',flat =True).distinct()
    #     text = valid[0] + '-' + valid[valid.count()-1]
    #     active[i]= text
        

    
    groups = list(dict.fromkeys(groups))
    fiscal = select_fiscal_year(request)
    calendar = select_calendar_year(request)
    months = select_month(request)

    vps = []
    vps = UmOscDeptUnitsReptV.objects.order_by('dept_grp_vp_area').values_list('dept_grp_vp_area_descr',flat =True).distinct()

        
        
    

    context = {
        'title': 'Summary of Charges',
        'depts': depts,
        'groups': groups,
        'groups_descr':groups_descr,
        'fiscal':fiscal,
        'calendar':calendar,
        'months':months,
        'vps': vps,
    }
    return HttpResponse(template.render(context,request))

@permission_required('oscauth.can_report', raise_exception=True)
def generate(request):
    depts = find_depts(request)
    grouping = ''
    unit = ''

    display_type = request.POST.get("unitGroupingGroup",None)
    
    if display_type in ['1']:
        grouping = 'Department ID'
        unit = request.POST.getlist('department_id')
        if request.POST.get('selectall',None) in ['2']:
            grouping = 'Department IDs'
            unit = depts
    elif display_type in ['3']:
        grouping = 'Department Group'
        unit = [request.POST.get('department_group')]
    elif display_type in ['4']:
        grouping = 'Department Group VP Area'
        unit = [request.POST.get('department_vp')]
    

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
        billing_period = billing_period + " " + request.POST.get('FIRSTYEAR') + " to"
        billing_period = billing_period + " " + request.POST.get('SECONDMONTH')
        billing_period = billing_period + " " + request.POST.get('SECONDYEAR')
    table = []
    if (unit != '' and billing_period != ''):
        rows = get_rows(unit, grouping, billing_period, dateRange, request)
        table = get_table(rows,request)
    if (table ==[] or list(table)[0][1]==0):
        if (table == []):
            rows = ''
        else:
            rows = 'There is no data for the current selection'
        table = []

    template = loader.get_template('soc-report.html')
    context = {
        'title': 'Summary of Charges',
        
        'grouping': grouping,
        'dateRange': dateRange,
        'unit': unit,
        'billing_period': billing_period,
        'rows': rows,
        'table': list(table),
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
    query = UmOscDeptUnitsReptV.objects.order_by('fiscal_yr').values_list('fiscal_yr',flat =True).distinct()
    return query.reverse()
    
def select_calendar_year(request):
    query = UmOscDeptUnitsReptV.objects.order_by('calendar_yr').values_list('calendar_yr',flat =True).distinct()
    return query.reverse()

def select_month(request):
    query = UmOscDeptUnitsReptV.objects.order_by('month').values_list('month',flat =True).distinct()
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
 	 		  'August', 'September', 'October', 'November', 'December']
    return query

def get_rows(unit, grouping, period, drange, request):
   

    if (drange == 'Fiscal Year'):
        values = UmOscDeptUnitsReptV.objects.filter(fiscal_yr__exact = period)
    elif (drange == 'Calendar Year'):
        values = UmOscDeptUnitsReptV.objects.filter(calendar_yr__exact = period)
    elif (drange == 'Single Month'):
        month = period.split(' ')[0]
        year = period.split(' ')[1]
        values = UmOscDeptUnitsReptV.objects.filter(calendar_yr__exact = year).filter(month__exact = month)
    elif (drange == 'Month-to-Month'):
        month1 = period.split(' ')[0]
        year1 = period.split(' ')[1]
        month2 = period.split(' ')[3]
        year2 = period.split(' ')[4]
        values = UmOscDeptUnitsReptV.objects.annotate(date = Concat('calendar_yr',Value(''), 'month')).filter(date__range = [year1+''+month1,year2+''+month2]).order_by('account').values('account','date').distinct()

    
    if (grouping == 'Department ID'):
        return values.filter(deptid__in = unit).order_by('account_desc').values().distinct()
    elif (grouping == 'Department IDs'):
        return values.filter(deptid__in = unit).order_by('account_desc').values().distinct()
    elif (grouping == 'Department Group'):
        return values.filter(dept_grp_descr__exact = unit[0]).order_by('account_desc').values().distinct()
    elif (grouping == 'Department Group VP Area'):
        return values.filter(dept_grp_vp_descr__exact = unit[0]).order_by('account_desc').values().distinct()

def get_table(rows,request):
    accounts = rows.values_list('account','account_desc').distinct()
    whole_table = []
    account_table = []
    final_table = []
    throwaway = []
    overall_cost = 0
    complete_table = []

    for i in accounts:
        services = accounts.filter(account__exact = i[0]).order_by('charge_group').values_list('description',flat = True)
        # account_total = 0
        # # account_table = []
        orders = services.filter(description__in = services).order_by('charge_group').values_list('charge_group', flat = True).distinct()
        total_cost =0.0
        whole_table = []
        for y in orders:
            charge_together = orders.filter(charge_group__exact = y).order_by('description').values_list('description','charge_code')
            charge_total = 0.0
            account_table = []
            
            for x in charge_together:
                samecode = charge_together.filter(charge_code__exact = x[1] or None).order_by('charge_code').values_list('unit_rate','quantity','amount','dept_descr','month').distinct()
                item_price = 0.0
                rate = 0.0
                quantity = 0
                
                for price in samecode:
                    if (price[0]==''):
                        rate = 0
                    else:
                        rate = float(price[0])
                    if (price[1]=='' or price[1] == None):
                        quantity= quantity +1
                    else:
                        quantity = quantity + int(price[1])
                    item_price =  item_price + float(price[2])
                    total_cost =  total_cost + float(price[2]) 
                charge_total = charge_total + item_price
                account_table.append([x[0],x[1],round(rate,2),quantity,round(item_price,2)])
            overall_cost = overall_cost + charge_total
            whole_table.append([y,account_table, round(charge_total,2)])
        final_table.append([i[0],i[1],whole_table,round(total_cost,2)])
    complete_table.append([final_table,round(overall_cost,2)])
    return complete_table


