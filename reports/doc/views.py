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
from project.pinnmodels import UmOscBillCycleV, UmOscDtDeptAcctListV, UmOscDeptProfileV, UmOscOtsCallSummaryV, UmOscAcctdetailMrcOccV, UmOscPhoneHistoryV, UmOscServiceLocV, UmOscRatedV
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
        'title': 'Detail of Charges',
        #'user_depts': user_depts,
        'names': names,
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
	bill_date = request.POST.get('billing_date')
	chartcoms = request.POST.getlist('chartcoms[]')

	# Formatting
	name = UmOscDeptProfileV.objects.filter(deptid=selected_dept)
	selected_dept = selected_dept + ' - ' + name[0].dept_name

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
				'subscriber_id': a.subscriber_id,
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
		monthly_query = UmOscAcctdetailMrcOccV.objects.filter(billing_date=date, account_number=cf, charge_type="MRC")
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


		# One Time Charges and Credits
		occ_charges = UmOscAcctdetailMrcOccV.objects.filter(billing_date=date, account_number=cf, charge_type="OCC")
		occ_rows = []
		occ_total = 0
		for c in occ_charges:
			if not any(r['work_order'] == c.package_code for r in occ_rows):
				row = {
					'work_order': c.package_code,
					'desc': 'Labor/Service Order and Equipment',
					'total_amt': c.charge_amount
				}
				occ_rows.append(row)
			else:
				row['total_amt'] += c.charge_amount
			occ_total += c.charge_amount
		for r in occ_rows:
			r['total_amt'] = '${:,.2f}'.format(r['total_amt'])

		
		data = {
			'account_number': cf,
			'type_summary': prefixes,
			'type_total': '${:,.2f}'.format(total),
			'charge_tables': charges,
			'monthly_data': monthly_data,
			'monthly_total': '${:,.2f}'.format(monthly_total),
			'occ': occ_rows,
			'occ_total':'${:,.2f}'.format(occ_total)
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
	chartcom = request.POST.get('chartcom:' + user_id)
	sub_id = request.POST.get('sub_id:' + user_id)
	charge_type = request.POST.get('charge_type:' + user_id)

	charge_type = 'Phone' # TEST - GET FROM OTHER PAGE

	# Fix date format - this is way too messy - make into a function
	date = bill_date.replace('.', '')
	date = date.replace(',', '')
	date = date.split(' ')
	date[0] = date[0][0:3]
	date = date[0] + ' ' + date[1] + ' ' + date[2]
	date = datetime.strptime(date, '%b %d %Y')
	date = str(date.year) + '-' + str(date.month) + '-' + str(date.day)

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

	# Return button functionality
	return_button = {
		'select_dept': selected_dept,
		'bill_date': bill_date,
		'chartcoms': format_chartcoms
	}

	# Find details for info box
	box_detail = UmOscPhoneHistoryV.objects.filter(user_defined_id=user_id, date_snapshot=date)
	if box_detail:
		username = box_detail[0].description
		phone_num = box_detail[0].phone_number
	else:
		username = 'No Name Match'

	total = 0

	# Monthly Charges table
	rows = []
	monthly_total = 0
	monthly_data = UmOscAcctdetailMrcOccV.objects.filter(account_number=chartcom, billing_date=date, charge_type="MRC", subscriber_id=sub_id)
	for m in monthly_data:
		if not any(r['item_code'] == m.item_code for r in rows):
			row = {
				'item_code': m.item_code,
				'desc': m.item_description,
				'unit_price': '${:,.2f}'.format(m.unit_price),
				'quantity': int(m.quantity),
				'total_charge': m.charge_amount
			}
			rows.append(row)
		else:
			row['quantity'] += int(m.quantity)
			row['total_charge'] += m.charge_amount
		monthly_total += m.charge_amount
	for r in rows:
		r['total_charge'] = '${:,.2f}'.format(r['total_charge'])
	total += monthly_total

	# Local and Toll Charges tables
	local = []
	toll = []
	local_total = 0
	toll_total = 0
	phone_num = user_id.split('-')
	phone_num = phone_num[1]
	rated_data = UmOscRatedV.objects.filter(subscriber_id=sub_id, from_number=phone_num, batch_date=date)
	for r in rated_data:
		if r.call_description == 'Local':
			l = {
				'connect_date': r.connect_date,
				'to_num': r.to_number,
				'location': r.place_name + ', ' + r.state_name,
				'duration': r.call_duration,
				'total_charge': r.amount_billed,
			}
			local_total += r.amount_billed
			l['total_charge'] = '${:,.2f}'.format(l['total_charge'])
			local.append(l)
		elif r.call_description == 'Toll':
			t = {
				'connect_date': r.connect_date,
				'to_num': r.to_number,
				'location': r.place_name + ', ' + r.state_name,
				'duration': r.call_duration,
				'total_charge': r.amount_billed,
			}
			toll_total += r.amount_billed
			t['total_charge'] = '${:,.2f}'.format(t['total_charge'])
			toll.append(t)
	total = total + local_total + toll_total


	context = {
		'title':'Detail of Charges',
		'dept': selected_dept,
		'billing_date': bill_date,
		'chartcoms': format_chartcoms,
		'user_id': user_id,
		'sub_id': sub_id,
		'chartcom': chartcom,
		'charge_type': charge_type,
		'username': username,
		'monthly_data': rows,
		'monthly_total': '${:,.2f}'.format(monthly_total),
		'local': local,
		'local_total': '${:,.2f}'.format(local_total),
		'toll': toll,
		'toll_total': '${:,.2f}'.format(toll_total),
		'total': '${:,.2f}'.format(total),
		'return_button': return_button
	}

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