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
from project.pinnmodels import UmOscBillCycleV, UmOscDtDeptAcctListV, UmOscDeptProfileV, UmOscOtsCallSummaryV, UmOscAcctdetailMrcOccV, UmOscPhoneHistoryV, UmOscServiceLocV, UmOscRatedV, UmOscRptSubscrib_Api_V
from oscauth.forms import *
from django.contrib.auth.decorators import login_required, permission_required

import json
from django.http import JsonResponse

from datetime import datetime
from django.shortcuts import redirect

from pages.models import Page

# Load intial Detail of Charge page
@permission_required('oscauth.can_report', raise_exception=True)
def get_doc(request):
    template = loader.get_template('doc.html')

    # # Find all departments user has access to
    names = list(AuthUserDept.get_report_departments(request))

    # Find associated chartfields
    if type(names[0]) is dict:
    	selected_dept = names[0]['deptid']
    else:
    	selected_dept = names[0].deptid
    dept_cfs = list((d.account_number for d in UmOscDtDeptAcctListV.objects.filter(deptid=selected_dept).order_by('account_number').distinct()))

    # Find all available billing dates
    billing_dates = list((d.billing_date for d in UmOscBillCycleV.objects.all().order_by('billing_date').reverse()))

    # Get instructions
    instructions = Page.objects.get(permalink='/doc')

    context = {
        'title': 'Telephony Detail of Charges',
        'form_action': '/reports/doc/report/',
        'names': names,
        'instructions': instructions,
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

	if not chartcoms:
		return HttpResponseRedirect('/reports/doc')

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
		all_data = UmOscOtsCallSummaryV.objects.filter(billing_date=date, account_number=cf).order_by('user_defined_id')
		prefixes = {}
		charges = {}
		total = 0
		for a in all_data:
			# Only include 'telephony'
			initial_prefix = a.user_defined_id.split('-')[0]
			prefix_query = UmOscRptSubscrib_Api_V.objects.filter(subscriber_prefix=initial_prefix)
			if (a.dtl_of_chrgs_telephony and (a.mrc_amount != 0 or a.tot_call_amount != 0)):
				# Determine user defined ID type
				if prefix_query:
					prefix = prefix_query[0].subscriber_desc
					if prefix == '':
						prefix = 'Misc.'
				else:
					prefix = 'Misc.'

				# Add new user defined ID type if applicable - telephony vs non telephony considered
				if prefix in prefixes:
					prefixes[prefix] += a.tot_amount
				else:
					prefixes[prefix] = a.tot_amount
				total += a.tot_amount

				# Create a telephony row for the charges table
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
				# Add row to appropriate table
				has_data = True
				charges[prefix]['rows'].append(user_id)
				charges[prefix]['total'] += user_id['total_charges']

		
		# Create Monthly Service Charges table
		monthly_query = UmOscAcctdetailMrcOccV.objects.filter(billing_date=date, account_number=cf, charge_type="MRC").order_by('item_code')
		monthly_data = {}
		monthly_total = 0
		for m in monthly_query:
			if m.dtl_of_chrgs_telephony:
				# Item code already exists in table
				if m.item_code in monthly_data:
					monthly_data[m.item_code]['quantity'] += int(m.quantity)
					monthly_data[m.item_code]['total'] += m.charge_amount
				# New item code for table
				else:
					monthly_data[m.item_code] = {
						'desc': m.item_description,
						'unit_amt': '${:,.2f}'.format(m.unit_price),
						'quantity': int(m.quantity),
						'total': m.charge_amount
					}
				has_data = True
				monthly_total += m.charge_amount

		
		# Make it look like money $$$$$
		for m in monthly_data.values():
			m['total'] = '${:,.2f}'.format(m['total'])

		for p in prefixes:
			prefixes[p] = '${:,.2f}'.format(prefixes[p])
		for c in charges:
			for r in charges[c]['rows']:
				if r['total_charges'] < 0:
					r['total_charges'] = '-' + '${:,.2f}'.format(abs(r['total_charges']))
				else:
					r['total_charges'] = '${:,.2f}'.format(r['total_charges'])
			charges[c]['total'] = '${:,.2f}'.format(charges[c]['total'])


		# Create One Time Charges, Work Order Summary, and Credits tables
		occ_charges = UmOscAcctdetailMrcOccV.objects.filter(billing_date=date, account_number=cf, charge_type="OCC").order_by('item_code')
		occ_rows = []
		occ_total = 0
		credits = []
		credit_total = 0
		otc_rows = []
		otc_total = 0
		for c in occ_charges:
			if c.dtl_of_chrgs_telephony:
				has_data = True
				# If OCC is a credit
				if c.charge_amount < 0:
					# New item code for table
					if not any (cr['item_code'] == c.item_code for cr in credits):
						credit = {
							'item_code': c.item_code,
							'credit': abs(c.charge_amount)
						}
						credits.append(credit)
					# Item code already exists in table
					for cr in credits:
						if cr['item_code'] == c.item_code:
							cr['credit'] += abs(c.charge_amount)
					credit_total += abs(c.charge_amount)
				# If OCC is a work order
				elif c.package_code:
					# New work order for table
					if not any(rw['work_order'] == c.package_code for rw in occ_rows):
						row = {
							'work_order': c.package_code,
							'total_amt': c.charge_amount,
							'equip': 0,
							'sol': 0
						}
						# If labor charge
						if c.item_code.startswith('LB'):
							row['sol'] = c.charge_amount
						# If Service Order/Equipment charge
						else:
							row['equip'] = c.charge_amount
						occ_rows.append(row)
					# Work order already exists in table
					else:
						for row in occ_rows:
							if row['work_order'] == c.package_code:
								row['total_amt'] += c.charge_amount
								# If equipment charge
								if c.item_code.startswith('LB'):
									row['sol'] += c.charge_amount
								# If Service Order/Labor charge
								else:
									row['equip'] += c.charge_amount
					occ_total += c.charge_amount
				# Create One Time Charges table
				else:
					# New item code for table
					if not any(rw['item_code'] == c.item_code for rw in otc_rows):
						row = {
							'item_code': c.item_code,
							'desc': c.item_description,
							'qty': int(c.quantity),
							'total': c.charge_amount
						}
						otc_rows.append(row)
					# Item code already exists in table
					else:
						for o in otc_rows:
							if o['item_code'] == c.item_code:
								o['qty'] += int(c.quantity)
								o['total'] += c.charge_amount
					otc_total += c.charge_amount


		# Make it look like money $$
		for r in occ_rows:
			r['total_amt'] = '${:,.2f}'.format(r['total_amt'])
			r['equip'] = '${:,.2f}'.format(r['equip'])
			r['sol'] = '${:,.2f}'.format(r['sol'])
		for c in credits:
			c['credit'] = '${:,.2f}'.format(c['credit'])
		for o in otc_rows:
			o['total'] = '${:,.2f}'.format(o['total'])

		
		# Add all tables to that chartfield
		data = {
			'account_number': cf,
			'data': has_data,
			'type_summary': prefixes,
			'type_total': '${:,.2f}'.format(total),
			'charge_tables': charges,
			'monthly_data': monthly_data,
			'monthly_total': '${:,.2f}'.format(monthly_total),
			'occ': occ_rows,
			'occ_total':'${:,.2f}'.format(occ_total),
			'credits':credits,
			'credit_total': '${:,.2f}'.format(credit_total),
			'otc': otc_rows,
			'otc_total': '${:,.2f}'.format(otc_total)
		}
		charge_types.append(data)
		has_data = False


	context= {
		'title':'Telephony Detail of Charges',
		'dept': selected_dept,
		'dept_mgr': dept_mgr,
		'dept_mgr_uniq': dept_mgr_uniq,
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
	dept_mgr = request.POST.get('dept_mgr')
	chartcoms = request.POST.get('chartcoms')
	user_id = request.POST.get('user_id')
	chartcom = request.POST.get('chartcom:' + user_id)
	sub_id = request.POST.get('sub_id:' + user_id)
	charge_type = request.POST.get('charge_type:' + user_id)

	# Fix date format
	date = format_date(bill_date)

	# Fix format of chartcom string list
	chartcoms = format_chartcoms(chartcoms)

	# Return button functionality
	return_dept = selected_dept.split(' ')[0]
	return_button = {
		'select_dept': return_dept,
		'bill_date': bill_date,
		'chartcoms': chartcoms
	}


	# Find details for info box
	box_detail = UmOscPhoneHistoryV.objects.filter(user_defined_id=user_id, date_snapshot=date)
	if box_detail:
		username = box_detail[0].description
		phone_num = box_detail[0].phone_number
	else:
		username = 'No Name Match'

	total = 0

	monthly_data = UmOscAcctdetailMrcOccV.objects.filter(billing_date=date, charge_type="MRC", subscriber_id=sub_id).order_by('item_code')
	toll_data = UmOscRatedV.objects.filter(subscriber_id=sub_id, batch_date=date, call_description="Toll").order_by('connect_date')
	local_data = UmOscRatedV.objects.filter(subscriber_id=sub_id, batch_date=date, call_description="Local").order_by('connect_date')

	chartfields = []

	# Find monthly charges
	for m in monthly_data:
		# New chartfield
		if not any(c['account'] == m.account_number for c in chartfields):
			chartfield = {
				'account': m.account_number,
				'monthly': [],
				'monthly_total': 0,
				'toll': [],
				'toll_total': 0,
				'local': [],
				'local_total': 0,
				'cf_total': 0
			}

			# Create a row of monthly data
			monthly_row = {
				'item_code': m.item_code,
	 			'desc': m.item_description,
	 			'unit_price': '${:,.2f}'.format(m.unit_price),
	 			'quantity': int(m.quantity),
 				'total_charge': m.charge_amount
			}
			chartfield['monthly'].append(monthly_row)
			chartfield['monthly_total'] += m.charge_amount
			chartfield['cf_total'] += m.charge_amount
			chartfields.append(chartfield)

		# Chartfield already accounted for
		else:
			for c in chartfields:
				if c['account'] == m.account_number:
					# New item code for table
					if not any(month['item_code'] == m.item_code for month in c['monthly']):
						# Create a row of monthly data
						monthly_row = {
							'item_code': m.item_code,
				 			'desc': m.item_description,
				 			'unit_price': '${:,.2f}'.format(m.unit_price),
				 			'quantity': int(m.quantity),
			 				'total_charge': m.charge_amount
						}
						c['monthly'].append(monthly_row)
					# Roll up by item code
					else:
						for x in c['monthly']:
							if x['item_code'] == m.item_code:
								x['quantity'] += int(m.quantity)
								x['total_charge'] += m.charge_amount
					c['monthly_total'] += m.charge_amount
					c['cf_total'] += m.charge_amount
		total += m.charge_amount

	# Find toll charges
	for t in toll_data:
		# Create new chartfield if necessary
		if not any(c['account'] == t.expense_account for c in chartfields):
			chartfield = {
				'account': t.expense_account,
				'monthly': [],
				'monthly_total': 0,
				'toll': [],
				'toll_total': 0,
				'local': [],
				'local_total': 0,
				'cf_total': 0
			}
			chartfields.append(chartfield)

		for c in chartfields:
			if c['account'] == t.expense_account:
				# Create a row of toll data
				toll_row = {
					'connect_date': t.connect_date,
		 			'to_num': t.to_number,
		 			'location': t.place_name + ', ' + t.state_name,
		 			'duration': t.call_duration,
					'total_charge': t.amount_billed
				}
				c['toll'].append(toll_row)
				c['toll_total'] += t.amount_billed
				c['cf_total'] += t.amount_billed
		total += t.amount_billed

	# Find local charges
	for l in local_data:
		# Creat new chartfield if necessary
		if not any(c['account'] == l.expense_account for c in chartfields):
			chartfield = {
				'account': l.expense_account,
				'monthly': [],
				'monthly_total': 0,
				'toll': [],
				'toll_total': 0,
				'local': [],
				'local_total': 0,
				'cf_total': 0
			}
			chartfields.append(chartfield)

		for c in chartfields:
			if c['account'] == l.expense_account:
				# Create a row of toll data
				local_row = {
					'connect_date': l.connect_date,
		 			'to_num': l.to_number,
		 			'location': l.place_name + ', ' + l.state_name,
		 			'duration': l.call_duration,
					'total_charge': l.amount_billed
				}
				c['local'].append(local_row)
				c['local_total'] += l.amount_billed
				c['cf_total'] += l.amount_billed
		total += l.amount_billed

	# Make everything look like money $$$$$
	for c in chartfields:
		c['monthly_total'] = '${:,.2f}'.format(c['monthly_total'])
		c['toll_total'] = '${:,.2f}'.format(c['toll_total'])
		c['local_total'] = '${:,.2f}'.format(c['local_total'])
		c['cf_total'] = '${:,.2f}'.format(c['cf_total'])

		for m in c['monthly']:
			m['total_charge'] = '${:,.2f}'.format(m['total_charge'])
		for t in c['toll']:
			t['total_charge'] = '${:,.2f}'.format(t['total_charge'])
		for l in c['local']:
			l['total_charge'] = '${:,.2f}'.format(l['total_charge'])


	context = {
		'title':'Telephony Detail of Charges',
		'dept': selected_dept,
		'billing_date': bill_date,
		'dept_mgr': dept_mgr,
		'chartcoms': chartcoms,
		'user_id': user_id,
		'sub_id': sub_id,
		'chartcom': chartcom,
		'charge_type': charge_type,
		'username': username,
		'total': '${:,.2f}'.format(total),
		'return_button': return_button,
		'chartfields': chartfields
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


# Return to DOC base
def restart(request):
	return redirect('reports/doc/')