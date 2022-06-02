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

from pages.models import Page

from order.models import StorageRate

# Load intial Detail of Charge page
@permission_required('oscauth.can_report', raise_exception=True)
def get_new(request):
    template = loader.get_template('doc.html')

    names = AuthUserDept.get_report_departments(request)

    # Find associated chartfields
    if type(names[0]) is dict:
        selected_dept = names[0]['deptid']
    else:
        selected_dept = names[0].deptid
    dept_cfs = list((d.account_number for d in UmOscDtDeptAcctListV.objects.filter(deptid=selected_dept).order_by('account_number').distinct()))

    # Find all available billing dates
    billing_dates = list((d.billing_date for d in UmOscBillCycleV.objects.all().order_by('billing_date').reverse()))

    # Get instructions
    instructions = Page.objects.get(permalink='/nonteleph')

    edit_dept = 'None'
    edit_date = 'None'
    edit_chartcom = 'None'
    if request.method =='POST':
        print(request.POST)
        # Get information from previous page
        edit_dept = request.POST.get('edit_dept')
        edit_date = request.POST.get('edit_date')
        # edit_chartcom = request.POST.get('edit_chartcom')
        # edit_chartcom = edit_chartcom[1:-1]
        # edit_chartcom = edit_chartcom.split(', ')
        # for e in edit_chartcom:
        #     print(e)

    context = {
        'title': "Non-Telephony Detail of Charges",
        'form_action': '/reports/nonteleph/report/',
        'names': names,
        'dates': billing_dates,
        'instructions': instructions,
        'initial_date':billing_dates[0],
        'dept_cfs': dept_cfs,

        'edit_dept': edit_dept,
        'edit_date': edit_date,
        'edit_chartcom': edit_chartcom
    }
    return HttpResponse(template.render(context,request))


def generate_report(request):
    template = loader.get_template('nonteleph.html')

    # Get information from previous page
    selected_dept = request.POST.get('select_dept')
    doc_depts = request.POST.get('select_dept')
    bill_date = request.POST.get('billing_date')
    chartcoms = request.POST.getlist('chartcoms[]')

    if not chartcoms:
        return HttpResponseRedirect('/reports/nonteleph')

    # Formatting
    name = UmOscDeptProfileV.objects.filter(deptid=selected_dept)
    selected_dept = selected_dept + ' - ' + name[0].dept_name

    dept_mgr = name[0].dept_mgr
    dept_mgr_uniq = name[0].dept_mgr_uniqname

    # Fix date format
    date = format_date(bill_date)

    # Fix chartfield format
    chartcoms = format_chartcoms(chartcoms)

    # Get MiServer and MiStorage Rates
    StorageRates= StorageRate.objects.filter(service=13)
    rates={}
    for rate in StorageRates:
        rates[rate.name]=rate.rate
    has_data = False
    charge_types = []
    for cf in chartcoms:
        # Create tables for each user defined ID type
        all_data = UmOscAcctdetailMrcOccV.objects.filter(billing_date=date, account_number=cf).order_by('unique_identifier', 'voucher_comment', 'item_description', 'invoice_date', 'user_defined_id')
        prefixes = {}
        charges = {}
        total = 0

        # MiServer/MiDatabase grouped row data
        # dictionary to save data beyond single row if same server
        retained = {}

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
                    'date': a.invoice_date,
                    'shortcode': a.shortcode,
                    'voucher_comment': a.voucher_comment,
                    'quantity_vouchered': a.quantity_vouchered,
                    'unique_id': a.unique_identifier,
                    'invoice_id': a.invoice_id
                }

                # MiServer/MiDatabase grouped row data
                # Consolidate server information, set new quality
                if prefix=='MiServer' or prefix=='MiDatabase':
                    if a.user_defined_id in retained:
                        retained[a.user_defined_id]['descr_jh'].append(a.item_description)
                        retained[a.user_defined_id]['quantity_vouchered_jh'].append(a.quantity_vouchered)
                        retained[a.user_defined_id]['rate_jh'].append(rates[a.item_code])
                        retained[a.user_defined_id]['total_charges_jh'].append(a.charge_amount)   
                    else:
                        retained[a.user_defined_id]={}
                        retained[a.user_defined_id]['descr_jh'] = [a.item_description]
                        retained[a.user_defined_id]['quantity_vouchered_jh'] = [a.quantity_vouchered]
                        retained[a.user_defined_id]['rate_jh'] = [rates[a.item_code]]
                        retained[a.user_defined_id]['total_charges_jh'] = [a.charge_amount]
                    
                    user_id['descr_jh']=retained[a.user_defined_id]['descr_jh']
                    user_id['quantity_vouchered_jh']=retained[a.user_defined_id]['quantity_vouchered_jh']
                    user_id['rate_jh']=retained[a.user_defined_id]['rate_jh']
                    user_id['total_charges_jh']=retained[a.user_defined_id]['total_charges_jh']

                # Add N/A
                if not user_id['project_name']:
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
                    elif prefix != 'Container Services' and prefix != 'MiStorage' and r['user_defined_id'] == a.user_defined_id and unit_price == '{:,.2f}'.format(a.unit_price):
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

        # MiServer/MiDatabase grouped row data
        # remove duplicate rows
        for c in charges:
            if c == 'MiServer' or c == 'MiDatabase':
                servers= []
                length = len(charges[c]['rows'])
                i=0
                while i < length:
                    target = charges[c]['rows'][i]
                    if target['user_defined_id'] in servers:
                        charges[c]['rows'].remove(target)
                        length -=1
                    else:
                        servers.append(target['user_defined_id'])
                        i+=1

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
        'title':"Non-Telephony Detail of Charges",
        'dept': selected_dept,
        'dept_mgr': dept_mgr,
        'dept_mgr_uniq': dept_mgr_uniq,
        'billing_date': bill_date,
        'charge_types': charge_types,
        'chartfields': chartcoms,

        'doc_depts': doc_depts,
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