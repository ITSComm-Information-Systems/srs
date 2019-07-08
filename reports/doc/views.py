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
from project.pinnmodels import UmOscBillCycleV, UmOscDtDeptAcctListV, UmOscDeptProfileV, UmOscOtsCallSummaryV
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
def generate_report(request):
	template = loader.get_template('doc-report.html')

	# Get information from previous page
	selected_dept = request.POST.get('select_dept')
	name = UmOscDeptProfileV.objects.filter(deptid=selected_dept)
	selected_dept = selected_dept + ' - ' + name[0].dept_name

	bill_date = request.POST.get('billing_date')
	chartcoms = request.POST.getlist('chartcoms[]')

	# Fix date format
	date = bill_date.replace('.', '')
	date = date.replace(',', '')
	date = datetime.strptime(date, '%b %d %Y')
	date = str(date.year) + '-' + str(date.month) + '-' + str(date.day)


	too_much_data = []

	# for cf in cfs:
	# 	test = UmOscOtsCallSummaryV.objects.filter(billing_date=date, account_number=cf)
	

	# Type of Charges
	for cf in chartcoms:
		all_data = UmOscOtsCallSummaryV.objects.filter(billing_date=date, account_number=cf)

		prefixes = {}
		total = 0
		for a in all_data:
			prefix = a.user_defined_id.split('-')
			prefix = prefix[0]
			if prefix in prefixes:
				prefixes[prefix] += a.tot_amount #Is this the right value??
			else:
				prefixes[prefix] = a.tot_amount
			total += a.tot_amount

		data = {
			'account_number': cf,
			'type_keys': prefixes.keys(),
			'type_summary': prefixes,
			'type_total': total
		}
		too_much_data.append(data)

	context= {
		'title':'Detail of Charges',
		'dept': selected_dept,
		'billing_date': bill_date,
		'cfs': too_much_data
	}

	return HttpResponse(template.render(context, request))

def show_detail(request):
	template = loader.get_template('doc-detail.html')

	context = {
		'title':'Detail of Charges'
	}

	return HttpResponse(template.render(context, request))

def show_tsr(request):
	template = loader.get_template('doc-tsr.html')

	context = {
		'title': 'Detail of Charges'
	}

	return HttpResponse(template.render(context, request))

def select_cf(request):
	selected_dept = request.GET.get('select_dept', None)
	dept_cfs = list(UmOscDtDeptAcctListV.objects.filter(deptid=selected_dept).order_by('account_number').values().distinct())

	name = UmOscDeptProfileV.objects.filter(deptid=selected_dept)
	name = {
		'name': name[0].dept_name
	}
	dept_cfs.append(name)

	return JsonResponse(dept_cfs, safe=False)