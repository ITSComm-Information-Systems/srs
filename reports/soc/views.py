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

from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV, UmOscDeptUnitsReptV
from oscauth.forms import *
import datetime
from django.contrib.auth.decorators import login_required, permission_required

from pages.models import Page


# Load selection page
@permission_required('oscauth.can_report', raise_exception=True)
def get_soc(request):
    template = loader.get_template('soc.html')

    # Get departments and department groups for dropdown
    depts = AuthUserDept.get_report_departments(request)
    groups_descr = UmOscDeptUnitsReptV.objects.order_by('dept_grp_descr').values_list('dept_grp_descr',flat = True).distinct()
    
    # Get date information for dropdowns
    fiscal = select_fiscal_year(request)
    calendar = select_calendar_year(request)
    months = select_month(request)

    dates = []
    today = datetime.date.today()
    for year in calendar:
        for month in months:
            if (month > today.month and int(year) == today.year) or int(year) > today.year:
                pass
            else:
                dates.append(num_to_words(month) + ' ' + year)

    # Get instructions
    instructions = Page.objects.get(permalink='/soc')

    # Get department group VP areas for dropdown
    vps = []
    vps = UmOscDeptUnitsReptV.objects.order_by('dept_grp_vp_area').values_list('dept_grp_vp_area_descr',flat =True).distinct() 

    context = {
        'title': 'Summary of Charges',
        'depts': depts,
        'groups_descr':groups_descr,
        'instructions': instructions,
        'fiscal':fiscal,
        'calendar':calendar,
        'months':months,
        'dates': dates,
        'vps': vps,
    }
    return HttpResponse(template.render(context,request))


# Generate report
@permission_required('oscauth.can_report', raise_exception=True)
def generate(request):
    # Get selected department(s) from form
    display_type = request.POST.get("unitGroupingGroup",None)
    grouping = ''
    unit = ''
    # If they selected by Department ID
    if display_type in ['1']:
        grouping = 'Department ID'
        if request.POST.get('deptall') == 'All':
            unit = 'All'
            format_unit = ['All']
        else:
            format_unit = request.POST.getlist('department_id')
            unit = remove_names(format_unit)
    # If they selected by Department Group
    elif display_type in ['3']:
        grouping = 'Department Group'
        unit = [request.POST.get('department_group')]
        format_unit = unit
    # If they selected by Department VP Group Area
    elif display_type in ['4']:
        grouping = 'Department Group VP Area'
        unit = [request.POST.get('department_vp')]
        format_unit = unit
    

    # Find billing range
    billing_period = ''
    dateRange = ''
    display_type = request.POST.get("dateRangeGroup",None)
    # If they selected by fiscal year
    if display_type in ['1']:
        dateRange = 'Fiscal Year'
        billing_period = request.POST.get('FISCALYEAR')
        format_billing_period = 'Fiscal Year ' + billing_period
    # If they selected by calendar year
    elif display_type in ['2']:
        dateRange = 'Calendar Year'
        billing_period = request.POST.get('CALENDARYEAR')
        format_billing_period = 'Calendar Year ' + billing_period
    # If they selected by single month
    elif display_type in ['3']:
        dateRange = 'Single Month'
        billing_period = request.POST.get('singlemonthselect')
        format_billing_period = billing_period
        month = words_to_num(billing_period.split(' ')[0])
        year = billing_period.split(' ')[1]
        billing_period = str(month) + ' ' + year
    # If they selected month-to-month
    elif display_type in ['4']:
        dateRange = 'Month-to-Month'
        billing_period1 = request.POST.get('multimonth1')
        billing_period2 = request.POST.get('multimonth2')
        month1 = words_to_num(billing_period1.split(' ')[0])
        month2 = words_to_num(billing_period2.split(' ')[0])
        year1 = billing_period1.split(' ')[1]
        year2 = billing_period2.split(' ')[1]
        billing_period = str(month1) + ' ' + year1 + ' to ' + str(month2) + ' ' + year2
        format_billing_period = billing_period1 + ' - ' + billing_period2


    # Get report data
    table = []
    if (unit != '' and billing_period != ''):
        # Pull Pinnacle data
        rows = get_rows(unit, grouping, billing_period, dateRange, request)
        # Format data
        table = get_table(rows,request)

    # If there is no data available for the selected dept & dates
    if (table == [] or list(table)[0][1] == 0):
        if (table == []):
            rows = ''
        else:
            rows = 'There is no data for the current selection'
        table = []

    print(len(table))

    template = loader.get_template('soc-report.html')
    context = {
        'title': 'Summary of Charges',   
        'grouping': grouping,
        'dateRange': dateRange,
        'unit': format_unit,
        'billing_period': format_billing_period,
        'num_months': find_num_months(dateRange, billing_period),
        'rows': rows,
        'table': list(table),
    }

    return HttpResponse(template.render(context,request))


# Grabs fiscal year options for dropdown
def select_fiscal_year(request):
    query = UmOscDeptUnitsReptV.objects.order_by('fiscal_yr').values_list('fiscal_yr',flat =True).distinct()
    return query.reverse()
    


# Grabs calendar year options for dropdown
def select_calendar_year(request):
    query = UmOscDeptUnitsReptV.objects.order_by('calendar_yr').values_list('calendar_yr',flat=True).distinct()
    return query.reverse()



# Grabs month options for dropdown
def select_month(request):
    query = UmOscDeptUnitsReptV.objects.order_by('month').values_list('month',flat=True).distinct()
    month_names = []
    query = query.reverse()
    for q in query:
        month_names.append(int(q))
    return month_names


# Calculates the number of months, given the billing period selected
def find_num_months(date_range, billing_period):
    if date_range == 'Fiscal Year' or date_range == 'Calendar Year':
        return 12
    elif date_range == 'Single Month':
        return 1
    else:
        total_months = 0

        # Parse selected billing period
        month1 = int(billing_period.split(' ')[0])
        year1 = int(billing_period.split(' ')[1])
        month2 = int(billing_period.split(' ')[3])
        year2 = int(billing_period.split(' ')[4])

        years_between = year2 - year1
        # If billing period is all within the same year
        if years_between == 0:
            total_months += month2 - month1 + 1
        # If months selected are in consecutive years
        elif years_between == 1:
            months_left_in_year = 12 - month1
            total_months += months_left_in_year + month2 + 1
        # If more than a year separates the dates
        else:
            months_left_in_year = 12 - month1
            months_between = 12 * (years_between - 1)
            total_months += months_left_in_year + months_between + month2 + 1

        return total_months



# Get data from Pinnacle based on selected department(s) and billing period
def get_rows(unit, grouping, period, drange, request):
    # unit = departments selected, grouping = how they selected dept, period = billing period, drange = how they selected billing period

    base_sql = '''select a.account, a.account_desc, a.charge_group, a.charge_code, a.description
            , round( nvl(avg(a.unit_rate),   sum(a.amount) /  sum( nvl(a.quantity,1) )  ),2)   as unit_rate
            , sum( nvl(a.quantity,1) ) as quantity
            , sum(a.amount) as amount
            from pinn_custom.UM_OSC_DEPT_UNITS_REPT_V a where '''


    end_sql = ''' group by a.account, a.account_desc, a.charge_group, a.charge_code,  a.description
                order by account_desc, charge_group, description '''

    parms = []

    # Filter report data by selected billing period
    if (drange == 'Fiscal Year'):
        date_sql =  ' a.fiscal_yr = %s '
        parms.append(period)

    elif (drange == 'Calendar Year'):
        date_sql =  ' a.calendar_yr = %s '
        parms.append(period)

    elif (drange == 'Single Month'):
        month = period.split(' ')[0]
        year = period.split(' ')[1]

        date_sql =  ' a.calendar_yr = %s and a.month = %s '
        parms.append(year)
        parms.append(month)

    elif (drange == 'Month-to-Month'):
        month1 = period.split(' ')[0]
        year1 = period.split(' ')[1]
        month2 = period.split(' ')[3]
        year2 = period.split(' ')[4]

        date_sql =  ' a.calendar_yr || a.month = %s between %s and %s '
        parms.append(year1 + month1)
        parms.append(year2 + month2)


    print(grouping)
    print(unit)
    if (grouping == 'Department ID'): #TODO
        if unit == "All":
            if request.user.has_perm("can_order_all"):
                dept_sql = ''
            else:
                depts = [d['deptid'] for d in AuthUserDept.get_report_departments(request)]
                dept_sql = ' and a.deptid in (%s) '
                parms.append(depts)
                #return values.filter(deptid__in = depts).order_by('account_desc').values().distinct()
        else:
            pass
            #return values.filter(deptid__in = unit).order_by('account_desc').values().distinct()

    elif (grouping == 'Department IDs'): #TODO
        dept_sql = ' and a.deptid in (%s) '
        parms.append(unit)
        print(unit)
        #return values.filter(deptid__in = unit).order_by('account_desc').values().distinct()

    elif (grouping == 'Department Group'):
        dept_sql = ' and a.dept_grp_descr = %s '
        parms.append(unit[0])

    elif (grouping == 'Department Group VP Area'):
        dept_sql = ' and a.dept_grp_vp_area_descr = %s '
        parms.append(unit[0])

    vals = UmOscDeptUnitsReptV.objects.raw(base_sql + date_sql + dept_sql + end_sql , parms)
    
    return vals


def get_table(rows,request):

    whole_table = []
    account_table = []
    final_table = []
    complete_table = []

    account = ''
    account_desc = ''
    charge_group = ''
    charge_total = 0
    total_cost = 0
    overall_cost = 0

    for row in rows:

        if row.charge_group != charge_group:
            if charge_group != '':
                whole_table.append([charge_group, account_table, charge_total])
            charge_group = row.charge_group
            charge_total = 0
            account_table = []

        if row.account != account:
            if account != '':
                final_table.append([account,account_desc,whole_table,total_cost])

            account = row.account
            account_desc = row.account_desc
            total_cost = 0
            whole_table = []

        account_table.append([row.description,row.charge_code,row.unit_rate,row.quantity,row.amount,2])
        charge_total = charge_total + row.amount
        total_cost = total_cost + row.amount
        overall_cost = overall_cost + row.amount

    whole_table.append([charge_group, account_table, charge_total])
    final_table.append([account,account_desc,whole_table,total_cost])
    complete_table.append([final_table,overall_cost])

    return complete_table


# Month conversion
def num_to_words(month):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    return months[month - 1]


# Month conversion
def words_to_num(month):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    for m in range(0, len(months)):
        if months[m] == month:
            if m + 1 < 10:
                return '0' + str(m + 1)
            else:
                return m + 1

# Gives selected departments without their names
def remove_names(unit):
    just_ids = []

    for u in unit:
        just_ids.append(u.split(' ')[0])

    return just_ids


