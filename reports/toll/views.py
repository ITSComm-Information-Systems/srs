import warnings
from datetime import datetime

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

from .models import UmTollCallDetail
from oscauth.models import AuthUserDept, Grantor, Role

from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV
from oscauth.forms import *

from datetime import datetime
from django.utils.dateparse import parse_date
from time import strptime

import os
from os import listdir
from project import settings

# Generate report
def generate(request):
	template = loader.get_template('tolls.html')

	dropdown = select_billing(request)
	depts = find_depts(request)

	# Set default billing period/dept ID
	bill_period = ''
	dept_id = ''
	if request.POST.get('bill_period') is None:
		bill_period = dropdown[0]
	else:
		bill_period = request.POST.get('bill_period')
	if request.POST.get('dept_id') is None:
		dept_id = depts[0]
	else:
		dept_id = request.POST.get('dept_id')

	dept = UmOscDeptProfileV.objects.filter(deptid=dept_id)
	dept_name = dept[0]

	inactive = False
	if dept[0].dept_eff_status == 'I':
		inactive = True

	month = bill_period.split(' ')[0]
	year = bill_period.split(' ')[1]

	context = {
		'periods': dropdown,
		'depts': depts,
		'dept_id': dept_id,
		'dept_name': dept_name,
		'inactive': inactive,
		'bill_period': bill_period,
		'bill_month': month,
		'bill_year': year
	}

	return HttpResponse(template.render(context, request))

# Select billing period and department ID
def select_billing(request):
 	template = loader.get_template('tolls.html')

 	billing_options = []

 	# # We should be able to do this without hardcoding...
 	months = ['null', 'January', 'February', 'March', 'April', 'May', 'June', 'July',
 	 		  'August', 'September', 'October', 'November', 'December']

 	og_format = os.listdir(settings.MEDIA_ROOT)
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

 	query = AuthUserDept.objects.filter(user=request.user.id).order_by('dept').exclude(dept='All').distinct('dept')

 	for dept in query:
 		if Group.objects.get(name=dept.group).name != 'Orderer':
 			depts.append(dept.dept)

 	return depts

# Generate report data
def generate_path(request, bill_date, deptid):
	date = bill_date.split('_');
	parsed_month = strptime(date[0], '%B').tm_mon
	parsed_year = strptime(date[-1], '%Y').tm_year
	string_date = ''
	if parsed_month > 9:
		string_date = str(parsed_year) + '_' + str(parsed_month) + '_20'
	else:
		string_date = str(parsed_year) + '_0' + str(parsed_month) + '_20'

	return string_date + '/' + string_date + '_' + deptid + '_Toll_Statement'

def download_PDF(request, bill_date, deptid):
	path = generate_path(request, bill_date, deptid) + '.pdf'
	file_path = os.path.join(settings.MEDIA_ROOT, path)
	if os.path.exists(file_path):
		with open(file_path, 'rb') as fh:
			response = HttpResponse(fh.read(), content_type="application/pdf")
			response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
			return response
		raise Http404
	else:
		return HttpResponse(file_path)

def download_cond_PDF(request, bill_date, deptid):
	path = generate_path(request, bill_date, deptid) + '_brief.pdf'
	file_path = os.path.join(settings.MEDIA_ROOT, path)
	if os.path.exists(file_path):
		with open(file_path, 'rb') as fh:
			response = HttpResponse(fh.read(), content_type="application/pdf")
			response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
			return response
		raise Http404
	else:
		return HttpResponse(file_path)

def download_CSV(request, bill_date, deptid):
	path = generate_path(request, bill_date, deptid) + '.csv'

	file_path = os.path.join(settings.MEDIA_ROOT, path)
	if os.path.exists(file_path):
		with open(file_path, 'rb') as fh:
			response = HttpResponse(fh.read(), content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
			return response
		raise Http404
	else:
		return HttpResponse(file_path)