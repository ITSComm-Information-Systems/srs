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
from django.urls import resolve

from ldap3 import Server, Connection, ALL

from project.pinnmodels import UmOscAcctsInUseV, UmOscAcctSubscribersV, UmOscDeptProfileV, UmOscAllActiveAcctNbrsV, UmOscAcctChangeInput, UmOscChartfieldV, UmOscAcctChangeRequest
from order.models import Chartcom
from oscauth.models import AuthUserDept, AuthUserDeptV
from datetime import datetime, date
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import F
from pages.models import Page

import json
from django.http import JsonResponse

import os
from django.db.models import indexes, Max
from django.db import connections
from django import db
import cx_Oracle

from django.core.mail import EmailMessage
from django.conf import settings
    
def homepage(request):

	notices = Page.objects.get(permalink='/notices')

	template = loader.get_template('home.html')

	context = {
		'title': 'Welcome to the Service Request System',
		'notices': notices,
	}
	return HttpResponse(template.render(context, request))

@permission_required(('oscauth.can_order'), raise_exception=True)
def chartchangeoptions(request):
	template = loader.get_template('chartchangeoptions.html')
	context = {
		'title': 'Chartfield Change Request',
	}
	return HttpResponse(template.render(context, request))

@permission_required(('oscauth.can_order'), raise_exception=True)
def chartchange(request):
	# Check for currently-running bill cycle
	curr = connections['pinnacle'].cursor()
	running = curr.callfunc('UM_OSC_UTIL_K.UM_IS_BILL_RUNNING_F', str)
	curr.close()

	if running == 'Y':
		template = loader.get_template('billingcycle.html')
		context = {
			'title': 'Chartfield Change Request',
		}
		return HttpResponse(template.render(context, request))

	# Not currently billing
	template = loader.get_template('chartchange.html')

	# Find initial department
	if request.user.has_perm('oscauth.can_report_all'):
		user_depts = UmOscDeptProfileV.objects.filter(deptid__iregex=r'^[0-9]*$').annotate(dept=F('deptid')).order_by('deptid')
	else:
		user_depts = AuthUserDept.get_order_departments(request.user.id)

	# Get notice
	notice = Page.objects.get(permalink='/ccr')
	context = {
		'title': 'Chartfield Change Request',
		'deptids': user_depts,
		'choose_cf_template': 'choose_cf.html',
		'choose_users_template': 'choose_users.html',
		'assign_new_template': 'assign_new.html',
		'review_submit_template': 'review_submit.html',
		'notice': notice
	}

	return HttpResponse(template.render(context, request))

@permission_required(('oscauth.can_order'), raise_exception=True)
def chartchangedept(request):
	# Check for currently-running bill cycle
	curr = connections['pinnacle'].cursor()
	running = curr.callfunc('UM_OSC_UTIL_K.UM_IS_BILL_RUNNING_F', str)
	curr.close()

	if running == 'Y':
		template = loader.get_template('billingcycle.html')
		context = {
			'title': 'Chartfield Change Request',
		}
		return HttpResponse(template.render(context, request))

	# Not currently billing
	template = loader.get_template('chartchangedept.html')

	# Find initial department
	if request.user.has_perm('oscauth.can_report_all'):
		user_depts = UmOscDeptProfileV.objects.filter(deptid__iregex=r'^[0-9]*$').annotate(dept=F('deptid')).order_by('deptid')
	else:
		user_depts = AuthUserDept.get_order_departments(request.user.id)

	# Get notice
	notice = Page.objects.get(permalink='/ccr')
	context = {
		'title': 'Chartfield Change Request (external department)',
		'deptids': user_depts,
		'all_dept': UmOscDeptProfileV.objects.filter(deptid__iregex=r'^[0-9]*$').annotate(dept=F('deptid')).order_by('deptid'),
		'choose_cf_dept_template': 'choose_cf_dept.html',
		'choose_users_dept_template': 'choose_users_dept.html',
		'assign_new_dept_template': 'assign_new_dept.html',
		'review_submit_dept_template': 'review_submit_dept.html',
		'notice': notice
	}

	return HttpResponse(template.render(context, request))

@permission_required(('oscauth.can_order'), raise_exception=True)
def managerapproval(request):
	id = request.GET.get("id")
	batch_info = UmOscAcctChangeRequest.objects.filter(batch=id).values('approved_by','rejected_by','date_added')[0]
	dept = UmOscAcctChangeRequest.objects.filter(batch=id)[0].new_dept_full_name.split()[0]
	allowed_mgr = list(AuthUserDept.objects.filter(dept=dept, group_id__in=[3, 4]).values_list('user_id', flat=True))

	date = batch_info['date_added']
	acceptor = batch_info['approved_by']
	rejector = batch_info['rejected_by']
	if (acceptor == '') and (rejector == ''):
		status = 'not_reviewed'
	else:
		status=''

	if ((request.user.id in allowed_mgr) or (request.user.is_superuser)):
		template = loader.get_template('managerapproval.html')
		context = {
			"title": "Manager Approval Form",
			'allowed_mgr': request.user.username,
			"status": status,
			"date": date,
			'acceptor': acceptor,
			'rejector': rejector,
			}
		return HttpResponse(template.render(context, request))
	else:
		template = loader.get_template('403.html')
		context = {"title": "Manager Approval Form"}
		return HttpResponse(template.render(context, request))

@permission_required(('oscauth.can_order'), raise_exception=True)
def managerapprovalinit(request):

	# Check for currently-running bill cycle
	curr = connections['pinnacle'].cursor()
	running = curr.callfunc('UM_OSC_UTIL_K.UM_IS_BILL_RUNNING_F', str)
	curr.close()

	if running == 'Y':
		template = loader.get_template('billingcycle.html')
		context = {
			'title': 'Chartfield Change Request',
		}
		return HttpResponse(template.render(context, request))

	id = request.GET.get("id")

	data = list(UmOscAcctChangeRequest.objects.filter(batch=id).values())
	# print('managerapprovalinit', data)
	return JsonResponse(data, safe=False)

@permission_required(('oscauth.can_order'), raise_exception=True)
def managerapprovalsubmit(request):
	post = request.POST
	print(post)
	status = post.get('status')
	id = post.get('request_id')
	change_row = UmOscAcctChangeRequest.objects.filter(batch=id)
	phone = list(change_row.values_list('user_defined_id', flat=True))
	approver = post.get('approver')
	uniqname = post.get('uniqname')
	
	if status == 'accepted':
		change_row.update(approved_by=approver)

		for x in change_row:
			new_entry = UmOscAcctChangeInput(
				uniqname = uniqname,
				user_defined_id = x.user_defined_id,
				mrc_account_number = x.mrc_account_number,
				toll_account_number = x.toll_account_number,
				local_account_number = x.local_account_number,
				date_added=date.today(),
				date_processed=None,
				messages=None,
				request_no=None,
				approved_by=approver
				)

			new_entry.save()

		# Add record to Pinnacle
		curr = connections['pinnacle'].cursor()
		datetime_added = date.today()
		curr.callproc('UM_CHANGE_ACCTS_BY_SUBSCRIB_K.UM_UPDATE_SUBSCRIB_FROM_WEB_P',[uniqname, datetime_added])
		curr.close()

		# # After Pinnacle is updated, send email
		subject = "Your Chartfield Change Request was approved"

		body = '''
Hello {uniqname}, 

Your chartfield change request for:
{phone}
 was approved by {approver}. '''.format(uniqname = uniqname, phone = phone, approver = approver)
		
		# to = [uniqname + '@umich.edu']
		to = ['mkokarde@umich.edu', 'hujingc@umich.edu', 'mazuelke@umich.edu', 'schenk@umich.edu', 'krips@umich.edu', 'karenh@umich.edu']


		email = EmailMessage(
			subject,
			body,
			'srs@umich.edu', # from email
			to,
			[]
		)

	elif status == 'rejected':
		change_row.update(rejected_by=approver)

		subject = "Your Chartfield Change Request was denied"

		body = '''
Hello {uniqname}, 

Your chartfield change request for:
 {phone} 
was denied by {approver}. '''.format(uniqname = uniqname, phone = phone, approver = approver)

		if post.get('rejectmessage')!='':
			body += 'The following message was included: ' + post.get('rejectmessage')
		
		# to = [uniqname + '@umich.edu']
		to = ['mkokarde@umich.edu', 'hujingc@umich.edu', 'mazuelke@umich.edu', 'schenk@umich.edu', 'krips@umich.edu', 'karenh@umich.edu']

		email = EmailMessage(
			subject,
			body,
			'srs@umich.edu', # from email
			to,
			[]
		)

	email.send()
	
	return JsonResponse({"success": True})

# Gives new chartfields when user changes department on page 1
# url chartchange/ajax/
@permission_required(('oscauth.can_order'), raise_exception=True)
def change_dept_1(request):
	selected_dept = request.GET.get('deptids', None)
	selected_dept = selected_dept.split(' - ')[0]

	# Find chartfield nickname
	chartcoms = Chartcom.objects.all()
	nicknames = {c.account_number:c.name for c in chartcoms}

	# Return all departments as options
	cf_options = list(UmOscAcctsInUseV.objects.filter(deptid=selected_dept).order_by('account_number').values())
	for i in cf_options:
		i['nickname']=nicknames.get(i["account_number"],'')
		db = UmOscAllActiveAcctNbrsV.objects.filter(account_number=i["account_number"])
		if db:
			i["short_code"] = db[0].short_code
			
	print('page1 cf_options:', cf_options)
	return JsonResponse(cf_options, safe=False)


# Gives new chartfields when user changes department on page 3
# url chartchangedept/ajax/
@permission_required(('oscauth.can_order'), raise_exception=True)
def change_dept_3(request):
	selected_dept = request.GET.get('deptids', None)

	# Get list of chartfields+shortcodes from department
	cf_options = dict(UmOscChartfieldV.objects.filter(deptid=selected_dept).values_list('chartfield','short_code'))
	chartcoms = Chartcom.objects.filter(dept=selected_dept)
	# add_chartcoms = UmOscChartfieldV.objects.filter(deptid=deptid)
	account_numbers = [c.account_number for c in chartcoms]
	results=[]
	for num in account_numbers:
		results.append({'account_number':num,'short_code':cf_options[num]})
	print('page 3 results: ',results)
	return JsonResponse(results, safe=False)


# Finds chartfield data when user changes chartfield
@permission_required(('oscauth.can_order'), raise_exception=True)
def get_cf_data(request):
	selected_cf = request.GET.get('selected', None)
	cf_data = list(UmOscAcctsInUseV.objects.filter(account_number=selected_cf).values())
	
	if not cf_data:
		cf_data = {'fund': 'missing'}
	return JsonResponse(cf_data, safe=False)


# Finds users for selected chartfield
# chartchange/update-table/
@permission_required(('oscauth.can_order'), raise_exception=True)
def get_users(request):
	# selected_cf = request.GET.get('selected', None).split(" ")[0]
	selected_cf = request.GET.get('selected', None)
	# Get info for selected chartfield
	cf = UmOscAcctsInUseV.objects.filter(account_number=selected_cf).values()
	print(cf)
	if cf:
		cf = cf[0]
	else:
		cf = {}
	
	# Get users
	cf_users = UmOscAcctSubscribersV.objects.filter(chartcom=cf.get("account_number", "")).order_by('user_defined_id')
	users = []
	for c in cf_users:
		user = {
			'user_defined_id':c.user_defined_id,
			'building':c.building,
			'toll_charged':c.toll_charged,
			'mrc_charged':c.mrc_charged,
			'local_charged':c.local_charged,
			'selected': False
		}
		if request.method == 'POST':
			user['selected'] = request.POST.get('select' + c.user_defined_id)
		users.append(user)
	return JsonResponse(users, safe=False)

# Submits change to database
@permission_required(('oscauth.can_order'), raise_exception=True)
def submit(request):
	template = loader.get_template('submitted.html')

	for key, value in request.POST.items():
		# Format of 'string' is user_defined_id//mrc_chartfield//toll_chartfield//local_chartfield
		string = request.POST.get(key)
		if '/' in string:
			strings = string.split('//')
			# Set toll and local to MRC if non-phone type
			if strings[2] == 'N/A':
				strings[2] = strings[1]
				strings[3] = strings[1]
			new_entry = UmOscAcctChangeInput(
				uniqname=request.user.username,
				user_defined_id=strings[0],
				mrc_account_number=strings[1],
				toll_account_number=strings[2],
				local_account_number=strings[3],
				date_added=date.today(),
				date_processed=None,
				messages=None,
				request_no=None)
			new_entry.save()

	# Add record to Pinnacle
	curr = connections['pinnacle'].cursor()
	uniqname = request.user.username
	datetime_added = date.today()
	curr.callproc('UM_CHANGE_ACCTS_BY_SUBSCRIB_K.UM_UPDATE_SUBSCRIB_FROM_WEB_P',[uniqname, datetime_added])
	curr.close()

	context = {
		'title': 'Chartfield Change',
	}

	return HttpResponse(template.render(context, request))


# Submits user request to table, sends email to manager
@permission_required(('oscauth.can_order'), raise_exception=True)
def submit_new(request):
	template = loader.get_template('submitteddept.html')
	# Changes per userid, lists
	user_defined_id = request.POST.getlist('user_id_form') # phone number
	building = request.POST.getlist('building_form')
	mrc_account_number = request.POST.getlist('mrc_form')
	toll_account_number = request.POST.getlist('toll_form')
	local_account_number = request.POST.getlist('local_form')

	# Same for all userids
	batch = UmOscAcctChangeRequest.objects.count() # batch id
	old_chartfield = request.POST.get('old_chartfield_form')
	new_chartfield = request.POST.get('new_chartfield_form')
	manager_url = settings.SITE_URL+"/managerapproval/?id=" + str(batch)
	user_full_name = request.POST.get('user_full_name_form')
	new_dept_full_name = request.POST.get('new_dept_full_name_form')
	rows = request.POST.get('num_rows')
	optional_message = request.POST.get('optional_message')
	if (optional_message != '') & (optional_message != None):
		message = "Included message: " + optional_message
	else:
		message = ""

	print(request.POST)
	
	for row in range(int(rows)+1):
		print(user_defined_id[row])
		new_entry = UmOscAcctChangeRequest(
			uniqname=request.user.username,
			user_defined_id=user_defined_id[row],
			building=building[row],
			mrc_account_number=mrc_account_number[row],
			toll_account_number=toll_account_number[row],
			local_account_number=local_account_number[row],
			old_dept_full_name=request.POST.get('old_dept_full_name_form'),
			old_dept_mgr=request.POST.get('old_dept_mgr_form'),
			old_chartfield=old_chartfield,
			old_shortcode=request.POST.get('old_shortcode_form'),
			user_full_name=user_full_name,
			new_dept_full_name=new_dept_full_name,
			new_dept_mgr=request.POST.get('new_dept_mgr_form'),
			new_chartfield=new_chartfield,
			new_shortcode=request.POST.get('new_shortcode_form'),
			optional_message=request.POST.get('optional_message'),
			date_added=date.today(),
			new_dept_mgr_uniqname=request.POST.get('new_dept_mgr_uniqname_form'),
			old_dept_mgr_uniqname=request.POST.get('old_dept_mgr_uniqname_form'),
			batch=batch)
		new_entry.save()

	# Get manager and proxy emails
	dept = new_dept_full_name.split()[0]
	allowed_mgr = list(AuthUserDept.objects.filter(dept=dept, group_id__in=[3, 4]).values_list('user_id', flat=True))
	email_list = ['mkokarde@umich.edu', 'hujingc@umich.edu', 'mazuelke@umich.edu', 'schenk@umich.edu', 'krips@umich.edu', 'karenh@umich.edu']

	# email_list = []
	# for id in allowed_mgr:
	# 	email_list.append(User.objects.get(id=id).email)

	subject = "SRS CCR test email"

	body = '''
Hello, 

{first} {last} from another department has requested to change a chartfield from {old_chartfield} to {new_chartfield}, which you have permissions over.
You may approve or deny this request here: {manager_url}. {message}

Thank you!'''.format(
		first = user_full_name.split(", ")[1],
		last = user_full_name.split(", ")[0], 
		old_chartfield = old_chartfield,
		new_chartfield = new_chartfield, 
		manager_url = manager_url,
		message=message,
	)

	to = email_list	

	email = EmailMessage(
		subject = subject,
		body = body,
		from_email = 'srs@umich.edu',
		to = to,
		reply_to = []
	)

	email.send()

	context = {
		'title': 'Chartfield Change',
	}

	return HttpResponse(template.render(context, request))

