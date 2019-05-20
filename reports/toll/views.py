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
#from .models import Role, Group, User
# from .forms import UserSuForm, AddUserForm
# from .utils import su_login_callback, custom_login_action, upsert_user
from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV
from oscauth.forms import *

from datetime import datetime
#from dateutil.relativedelta import relativedelta
from django.utils.dateparse import parse_date
from time import strptime



# Generate report
def generate(request):
	template = loader.get_template('tolls.html')

	dropdown = select_billing(request)
	depts = find_depts(request)
	pdf =  'From' #PDF_report(request)
	cond_pdf = 'Elsewhere!' #condPDF_report(request)
	csv = 'Pull' #CSV_report(request)
	links = "https://www.itcom.itd.umich.edu/osc/tollstmts/getfile.php?file=" + generate_data(request) + "_Toll_Statement"
	context = {
	'periods': dropdown,
	'depts': depts,
	'pdf': links + ".pdf",
	'cond_pdf': links + "_breif.pdf",
	'csv': links + ".csv",

	}

	return HttpResponse(template.render(context, request))

# Select billing period and department ID
def select_billing(request):
 	template = loader.get_template('tolls.html')

 	billing_options = []
 	current_period = datetime.now() - relativedelta(months=1)
 	for i in range(0, 13):
 		month = current_period - relativedelta(months=i)
 		text = format(month, '%B %Y')
 		billing_options.append(text)

 	return billing_options
 	#return HttpResponse(template.render(context, request))

 # List all departments
def find_depts(request):
 	depts = []

 	query = AuthUserDept.objects.filter(user=request.user.id).order_by('dept').exclude(dept='All').distinct('dept')

 	for dept in query:
 		if Group.objects.get(name=dept.group).name != 'Orderer':
 			depts.append(dept.dept)

 	return depts

# Generate report data
def generate_data(request):
	if request.POST.get('bill_period') is None:
		## make default the most recent one 
		return 'temp'
	else:
		# ITS Comm Monthly Charge Summary totals of all charges by userID
		date = ''
		dept_id = ''
		if request.method == 'POST':
			date = request.POST.get('bill_period').split()
			dept_id = request.POST.get('dept_id')

		parsed_month = strptime(date[0], '%B').tm_mon
		parsed_year = strptime(date[-1], '%Y').tm_year
		if parsed_month > 9:
			string_date = str(parsed_year) + '_' + str(parsed_month) + '_20_'
		else:
			string_date = str(parsed_year) + '_0' + str(parsed_month) + '_20_'
		#bill_date = parse_date(string_date)
		

		return string_date + str(dept_id)

# # Provide downloadable PDF report
# def PDF_report(request):

# 	return 'Test'

# # Provide downloadable condensed PDF report
# def condPDF_report(request):
# 	return 'Test'

# # Provide downloadable CSV report
# def CSV_report(request):
# 	return 'Test'
