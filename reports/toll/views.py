import warnings
from datetime import datetime
import json

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

from .models import UmTollCallDetail,DownloadLog
from oscauth.models import AuthUserDept, Grantor, Role, AuthUserDeptV

from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime
from django.utils.dateparse import parse_date
from time import strptime
import os
from os import listdir
from project import settings

from pages.models import Page

# Generate report
@permission_required('oscauth.can_report', raise_exception=True)
def select(request):
	template = loader.get_template('tolls.html')

	dropdown = select_billing(request)
	depts = find_depts(request)
	dept_names = []

	# Get instructions
	instructions = Page.objects.get(permalink='/toll')
	
	edit_dept = 'None'
	edit_date = 'None'
	if request.method =='POST':
        # Get information from previous page
		edit_dept = request.POST.get('edit_dept')
		edit_date = request.POST.get('edit_date')

	context = {
		'title': 'Toll Statements',
		'periods': dropdown,
		'depts': depts,	
		'instructions': instructions,
		'dept_names': dept_names,

		'edit_dept': edit_dept,
        'edit_date': edit_date
	}

	return HttpResponse(template.render(context, request))


@permission_required('oscauth.can_report', raise_exception=True)
def generate(request):
	template = loader.get_template('tolls-downloads.html')
	# Set default billing period/dept ID
	bill_period = ''
	dept_id = ''
	submit = True
	
	bill_period = request.POST.get('bill_period')

	if not bill_period:
		return HttpResponseRedirect('/reports/tolls')
		
	dept_id = request.POST.get('dept_id').split('-')[0]

	dept = UmOscDeptProfileV.objects.filter(deptid=dept_id)
	dept_name = dept[0].dept_name
	dept_mgr = dept[0].dept_mgr
	dept_mgr_uniq = dept[0].dept_mgr_uniqname


	inactive = False
	if dept[0].dept_eff_status == 'I':
		inactive = True

	month = bill_period.split(' ')[0]
	year = bill_period.split(' ')[1]

	context = {
		'title': "Toll Statements",
		'dept_id': dept_id,
		'dept_name': dept_name,
		'dept_mgr': dept_mgr,
		'dept_mgr_uniq':dept_mgr_uniq,
		'inactive': inactive,
		'bill_period': bill_period,
		'bill_month': month,
		'bill_year': year,
		'submit': submit,

		'edit_dept': dept_id,
		'edit_date': bill_period
	}

	return HttpResponse(template.render(context, request))
	


# Select billing period and department ID
@permission_required('oscauth.can_report', raise_exception=True)
def select_billing(request):
 	billing_options = []

 	# # We should be able to do this without hardcoding...
 	months = ['null', 'January', 'February', 'March', 'April', 'May', 'June', 'July',
 	 		  'August', 'September', 'October', 'November', 'December']

 	og_format = os.listdir(settings.MEDIA_ROOT + '/toll')
 	og_format.sort()
 	for date in og_format:
 		pieces = date.split('_')
 		year = pieces[0]
 		month_num = pieces[1]
 		month = months[int(month_num)]
 		text = month + ' ' + str(year)
 		billing_options.append(text)
 	billing_options.reverse()

 	return billing_options


 # List all departments
def find_depts(request):
	depts = []
		
	# query = AuthUserDeptV.objects.filter(user=request.user.id, codename='can_report').order_by('dept').exclude(dept='All').distinct('dept')

	# for dept in query:
	# 	#if Group.objects.get(name=dept.group).name != 'Orderer':
	# 	name = UmOscDeptProfileV.objects.filter(deptid=dept.dept)[0].dept_name
	# 	#depts.append(dept.dept)
	# 	depart = {
	# 		'id': dept.dept,
	# 		'name': name
	# 	}
	# 	depts.append(depart)
	depts = AuthUserDept.get_report_departments(request)
	return depts

# Generate report data
def generate_path(request, bill_date, deptid):
	date = bill_date.split('_')
	parsed_month = strptime(date[0], '%B').tm_mon
	parsed_year = strptime(date[-1], '%Y').tm_year
	string_date = ''
	if parsed_month > 9:
		string_date = str(parsed_year) + '_' + str(parsed_month) + '_20'
	else:
		string_date = str(parsed_year) + '_0' + str(parsed_month) + '_20'

	return string_date + '/' + string_date + '_' + deptid + '_Toll_Statement'


@permission_required('oscauth.can_report', raise_exception=True)
def download_PDF(request, bill_date, deptid):
	path = generate_path(request, bill_date, deptid) + '.pdf'
	file_path = os.path.join(settings.MEDIA_ROOT + '/toll/', path)

	if os.path.exists(file_path):
		with open(file_path, 'rb') as fh:
			response = HttpResponse(fh.read(), content_type="application/pdf")
			response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
			return response
		raise Http404
	else:
		return HttpResponse(file_path)


@permission_required('oscauth.can_report', raise_exception=True)
def download_cond_PDF(request, bill_date, deptid):
	path = generate_path(request, bill_date, deptid) + '_brief.pdf'
	file_path = os.path.join(settings.MEDIA_ROOT + '/toll/',path)
	if os.path.exists(file_path):
		with open(file_path, 'rb') as fh:
			response = HttpResponse(fh.read(), content_type="application/pdf")
			response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
			return response
		raise Http404
	else:
		return HttpResponse(file_path)


@permission_required('oscauth.can_report', raise_exception=True)
def download_CSV(request, bill_date, deptid):
	path = generate_path(request, bill_date, deptid) + '.csv'

	file_path = os.path.join(settings.MEDIA_ROOT + '/toll/', path)
	if os.path.exists(file_path):
		with open(file_path, 'rb') as fh:
			response = HttpResponse(fh.read(), content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
			return response
		raise Http404
	else:
		return HttpResponse(file_path)
	
@permission_required('oscauth.can_report', raise_exception=True)
@csrf_exempt
def log_report_download(request):
	if request.method != 'POST':
		return HttpResponseBadRequest('Invalid request method')
	request_body = request.body.decode('utf-8')
	try:
		data = json.loads(request_body)
	except json.JSONDecodeError:
		return HttpResponseBadRequest('Invalid JSON in request body')
	
	report_type = data.get('report_type')
	bill_month = data.get('bill_month')
	bill_year = data.get('bill_year')
	dept_id = data.get('dept_id')
	print(report_type,bill_month,bill_year,dept_id)

	log_event = DownloadLog(
		report_type = report_type,
		bill_year = bill_year,
		bill_month = bill_month,
		dept_id = dept_id
	)

	log_event.save()
	
	return HttpResponse("logged", status=200)