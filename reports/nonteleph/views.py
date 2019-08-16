import warnings

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

from oscauth.models import AuthUserDept, AuthUserDeptV
from project.pinnmodels import UmOscBillCycleV, UmOscDtDeptAcctListV, UmOscDeptProfileV, UmOscAcctdetailMrcOccV, UmOscRptSubscrib_Api_V
from oscauth.forms import *
from django.contrib.auth.decorators import login_required, permission_required

from datetime import datetime
from django.shortcuts import redirect

# Load intial Detail of Charge page
@permission_required('oscauth.can_report', raise_exception=True)
def get_new(request):
    template = loader.get_template('doc.html')

    # Find all departments user has access to
    user_depts = (d.dept for d in AuthUserDeptV.objects.filter(user=request.user.id,codename='can_report').order_by('dept').exclude(dept='All').distinct('dept'))
    user_depts = list(user_depts)

    # Find dept names
    names = []
    name_query = list(d.dept_name for d in UmOscDeptProfileV.objects.filter(deptid__in=user_depts).order_by('deptid'))
    for i in range(0, len(user_depts)):
    	name = {
    		'deptid': user_depts[i],
    		'name': name_query[i]
    	}
    	names.append(name)

    # Find associated chartfields
    selected_dept = user_depts[0]
    dept_cfs = list((d.account_number for d in UmOscDtDeptAcctListV.objects.filter(deptid=selected_dept).order_by('account_number').distinct()))

    # Find all available billing dates
    billing_dates = list((d.billing_date for d in UmOscBillCycleV.objects.all().order_by('billing_date').reverse()))

    context = {
        'title': "Other Detail of Charges",
        'form_action': '/reports/nonteleph/report/',
        'names': names,
        'dates': billing_dates,
        'initial_date':billing_dates[0],
        'dept_cfs': dept_cfs
    }
    return HttpResponse(template.render(context,request))


def generate_report(request):
    template = loader.get_template('nonteleph.html')

    # Get information from previous page
    selected_dept = request.POST.get('select_dept')
    bill_date = request.POST.get('billing_date')
    chartcoms = request.POST.getlist('chartcoms[]')

    # Formatting
    name = UmOscDeptProfileV.objects.filter(deptid=selected_dept)
    selected_dept = selected_dept + ' - ' + name[0].dept_name

    dept_mgr = name[0].dept_mgr
    dept_mgr_uniq = name[0].dept_mgr_uniqname

    # Fix date format
    date = format_date(bill_date)

    # Fix chartfield format
    chartcoms = format_chartcoms(chartcoms)


    has_data = False
    charge_types = []
    for cf in chartcoms:
        # Create tables for each user defined ID type
        all_data = UmOscAcctdetailMrcOccV.objects.filter(billing_date=date, account_number=cf).order_by('voucher_comment', 'item_description', 'invoice_date')
        prefixes = {}
        charges = {}
        total = 0
        for a in all_data:
            initial_prefix = a.user_defined_id.split('-')[0]
            prefix_query = UmOscRptSubscrib_Api_V.objects.filter(subscriber_prefix=initial_prefix)
            # Only include non-telephony
            if a.dtl_of_chrgs_nontelephony:
                # Determine user defined ID type
                if prefix_query:
                    prefix = prefix_query[0].subscriber_desc
                    if prefix == '':
                        prefix = 'Misc.'
                else:
                    prefix = 'Misc.'

                # Add new user defined ID type if applicable
                if prefix in prefixes:
                    prefixes[prefix] += a.charge_amount
                else:
                    prefixes[prefix] = a.charge_amount
                total += a.charge_amount

                # Create a non-telephony row for the charges table
                user_id = {
                    'user_defined_id': a.user_defined_id,
                    'descr': a.item_description,
                    'qty': int(a.quantity),
                    'total_charges': a.charge_amount,
                    'project_name': a.unique_identifier,
                    'date': a.invoice_date
                }
                # Add N/A
                if  not user_id['project_name']:
                    user_id['project_name'] = 'N/A'
                # Determine charge vs credit
                if a.unit_price < 0:
                    user_id['type'] = 'Credit'
                    user_id['unit_price'] = '-' + '${:,.2f}'.format(abs(a.unit_price))
                else:
                    user_id['type'] = 'Charge'
                    user_id['unit_price'] = '${:,.2f}'.format(a.unit_price)

                # Add to prefix table if it doesn't exist    
                if prefix not in charges:
                    charges[prefix] = {
                        'rows': [],
                        'total': 0
                    }
                
                has_data = True
                # Roll up charges/credits
                has_data = True
                breakout = False
                for r in charges[prefix]['rows']:
                    unit_price = r['unit_price'].replace('$', '')
                    # Container Services
                    if prefix == 'Container Services' and r['project_name'] == a.unique_identifier and r['descr'] == a.item_description and unit_price == '{:,.2f}'.format(a.unit_price):
                        r['qty'] += int(a.quantity)
                        r['total_charges'] += a.charge_amount
                        breakout = True
                    # Non-container Services
                    elif prefix != 'Container Services' and r['user_defined_id'] == a.user_defined_id and unit_price == '{:,.2f}'.format(a.unit_price):
                        r['qty'] += int(a.quantity)
                        r['total_charges'] += a.charge_amount
                        breakout = True
                if breakout == False:
                    charges[prefix]['rows'].append(user_id)

                charges[prefix]['total'] += user_id['total_charges']

    
        for p in prefixes:
            prefixes[p] = '${:,.2f}'.format(prefixes[p])
        for c in charges:
            for r in charges[c]['rows']:
                if r['total_charges'] < 0:
                    r['total_charges'] = '-' + '${:,.2f}'.format(abs(r['total_charges']))
                else:
                    r['total_charges'] = '${:,.2f}'.format(r['total_charges'])
            charges[c]['total'] = '${:,.2f}'.format(charges[c]['total'])

        
        # Add all tables to that chartfield
        data = {
            'account_number': cf,
            'data': has_data,
            'type_summary': prefixes,
            'type_total': '${:,.2f}'.format(total),
            'charge_tables': charges
        }
        charge_types.append(data)
        has_data = False


    context= {
        'title':"Other Detail of Charges",
        'dept': selected_dept,
        'dept_mgr': dept_mgr,
        'dept_mgr_uniq': dept_mgr_uniq,
        'billing_date': bill_date,
        'charge_types': charge_types,
        'chartfields': chartcoms
    }

    return HttpResponse(template.render(context, request))


# Format date for query use
def format_date(bill_date):
    date = bill_date.replace('.', '')
    date = date.replace(',', '')
    date = date.split(' ')
    date[0] = date[0][0:3]
    date = date[0] + ' ' + date[1] + ' ' + date[2]
    date = datetime.strptime(date, '%b %d %Y')
    date = str(date.year) + '-' + str(date.month) + '-' + str(date.day)
    return date

# Format chartcoms as list
def format_chartcoms(chartcoms):
    chartcoms = str(chartcoms)
    chartcoms = chartcoms.replace('"','')
    chartcoms = chartcoms.replace('[','')
    chartcoms = chartcoms.replace(']','')
    chartcoms = chartcoms.replace(',','')
    chartcoms = chartcoms.replace(' ', '')
    chartcoms = chartcoms.split('\'')
    format_chartcoms = []
    for c in chartcoms:
        if len(c) != 0:
            format_chartcoms.append(c)
    return format_chartcoms