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

from oscauth.models import AuthUserDept
# from .models import Role, Group, User
# from .forms import UserSuForm, AddUserForm
# from .utils import su_login_callback, custom_login_action, upsert_user
from project.pinnmodels import UmOscBillCycleV, UmOscDtDeptAcctListV, UmOscDeptProfileV, UmOscOtsCallSummaryV, UmOscAcctdetailMrcOccV
from oscauth.forms import *
from django.contrib.auth.decorators import login_required, permission_required

import json
from django.http import JsonResponse

from datetime import datetime

# Load intial Detail of Charge page
@permission_required('oscauth.can_report', raise_exception=True)
def get_doc(request):
    template = loader.get_template('doc.html')

    # Find all departments user has access to
    user_depts = (d.dept for d in AuthUserDept.objects.filter(user=request.user.id).order_by('dept').exclude(dept='All').distinct('dept'))
    user_depts = list(user_depts)

    # Initial dept name
    name = UmOscDeptProfileV.objects.filter(deptid=user_depts[0])

    # Find associated chartfields
    selected_dept = user_depts[0]
    dept_cfs = list((d.account_number for d in UmOscDtDeptAcctListV.objects.filter(deptid=selected_dept).order_by('account_number').distinct()))

    # Find all available billing dates
    billing_dates = list((d.billing_date for d in UmOscBillCycleV.objects.all().order_by('billing_date').reverse()))

    context = {
        'title': 'Detail of Charges',
        'user_depts': user_depts,
        'name': name[0].dept_name,
        'dates': billing_dates,
        'initial_date':billing_dates[0],
        'dept_cfs': dept_cfs
    }
    return HttpResponse(template.render(context,request))



# Generate basic report based on user selections
@permission_required('oscauth.can_report', raise_exception=True)
def generate_report(request):
	template = loader.get_template('doc-report.html')

	# Get information from previous page
	selected_dept = request.POST.get('select_dept')
	name = UmOscDeptProfileV.objects.filter(deptid=selected_dept)
	selected_dept = selected_dept + ' - ' + name[0].dept_name

	bill_date = request.POST.get('billing_date')
	chartcoms = request.POST.getlist('chartcoms[]')

	# Fix date format - this is way too messy
	date = bill_date.replace('.', '')
	date = date.replace(',', '')
	date = date.split(' ')
	date[0] = date[0][0:3]
	date = date[0] + ' ' + date[1] + ' ' + date[2]
	date = datetime.strptime(date, '%b %d %Y')
	date = str(date.year) + '-' + str(date.month) + '-' + str(date.day)


	charge_types = []
	for cf in chartcoms:
		all_data = UmOscOtsCallSummaryV.objects.filter(billing_date=date, account_number=cf).order_by('user_defined_id')

		prefixes = {}
		charges = {}
		total = 0
		for a in all_data:
			prefix = a.user_defined_id.split('-')
			prefix = prefix[0]

			# Type of charges
			if prefix in prefixes:
				prefixes[prefix] += a.tot_amount
			else:
				prefixes[prefix] = a.tot_amount
			total += a.tot_amount

			# Charge tables
			user_id = {
				'user_defined_id': a.user_defined_id,
				'monthly_charges': '${:,.2f}'.format(a.mrc_amount),
				'call_number': a.tot_call_count,
				'call_amount': '${:,.2f}'.format(a.tot_call_amount),
				'total_charges': a.tot_amount
			}
			if prefix not in charges:
				charges[prefix] = {
					'rows': [],
					'total': 0
				}
			charges[prefix]['rows'].append(user_id)
			charges[prefix]['total'] += user_id['total_charges']

		
		# Monthly Service Charges table
		monthly_query = UmOscAcctdetailMrcOccV.objects.filter(billing_date=date, account_number=cf)
		monthly_data = {}
		monthly_total = 0
		for m in monthly_query:
			if m.item_code in monthly_data:
				monthly_data[m.item_code]['quantity'] += int(m.quantity)
				monthly_data[m.item_code]['total'] += m.charge_amount
			else:
				monthly_data[m.item_code] = {
					'desc': m.item_description,
					'unit_amt': '${:,.2f}'.format(m.unit_price),
					'quantity': int(m.quantity),
					'total': m.charge_amount
				}
				monthly_total += m.charge_amount

		
		# Make it look like money $$$$$
		for m in monthly_data.values():
			m['total'] = '${:,.2f}'.format(m['total'])

		for p in prefixes:
			prefixes[p] = '${:,.2f}'.format(prefixes[p])
		for c in charges:
			for r in charges[c]['rows']:
				r['total_charges'] = '${:,.2f}'.format(r['total_charges'])
			charges[c]['total'] = '${:,.2f}'.format(charges[c]['total'])

		
		data = {
			'account_number': cf,
			'type_summary': prefixes,
			'type_total': '${:,.2f}'.format(total),
			'charge_tables': charges,
			'monthly_data': monthly_data,
			'monthly_total': '${:,.2f}'.format(monthly_total)
		}
		charge_types.append(data)

	context= {
		'title':'Detail of Charges',
		'dept': selected_dept,
		'billing_date': bill_date,
		'charge_types': charge_types,
		'chartfields': chartcoms
	}

	return HttpResponse(template.render(context, request))



@permission_required('oscauth.can_report', raise_exception=True)
def show_detail(request):
	template = loader.get_template('doc-detail.html')

	# Get information from previous page
	selected_dept = request.POST.get('selected_dept')
	bill_date = request.POST.get('billing_date')
	chartcoms = request.POST.get('chartcoms')
	user_id = request.POST.get('user_id')

	# Fix format of chartcom string list - this is messy
	chartcoms = chartcoms.replace('[','')
	chartcoms = chartcoms.replace(']','')
	chartcoms = chartcoms.replace(',','')
	chartcoms = chartcoms.replace(' ', '')
	chartcoms = chartcoms.split('\'')
	format_chartcoms = []
	for c in chartcoms:
		if len(c) != 0:
			format_chartcoms.append(c)


	context = {
		'title':'Detail of Charges',
		'dept': selected_dept,
		'billing_date': bill_date,
		'chartcoms': format_chartcoms,
		'user_id': user_id
	}

	#return JsonResponse(context, safe=False)
	return HttpResponse(template.render(context, request))



@permission_required('oscauth.can_report', raise_exception=True)
def show_tsr(request):
	template = loader.get_template('doc-tsr.html')

	context = {
		'title': 'Detail of Charges'
	}

	return HttpResponse(template.render(context, request))



@permission_required('oscauth.can_report', raise_exception=True)
def select_cf(request):
	selected_dept = request.GET.get('select_dept', None)
	dept_cfs = list(UmOscDtDeptAcctListV.objects.filter(deptid=selected_dept).order_by('account_number').values().distinct())

	name = UmOscDeptProfileV.objects.filter(deptid=selected_dept)
	name = {
		'name': name[0].dept_name
	}
	dept_cfs.append(name)

	return JsonResponse(dept_cfs, safe=False)