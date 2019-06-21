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

from ldap3 import Server, Connection, ALL

from project.pinnmodels import UmOscAcctsInUseV, UmOscAcctSubscribersV, UmOscDeptProfileV
from oscauth.models import AuthUserDept
from datetime import datetime

def chartchange(request):
	template = loader.get_template('chartchange.html')

	
	# Find all departments user has access to
	user_depts = (d.dept for d in AuthUserDept.objects.filter(user=request.user.id).order_by('dept').exclude(dept='All').distinct('dept'))
	user_depts = list(user_depts)
	default_dept = user_depts[0]

	select_dept = default_dept

	# Get dept info from selected dept
	query = UmOscDeptProfileV.objects.filter(deptid=select_dept)
	old_obj = query[0]
	dept_info = {
		'dept_id': select_dept,
		'dept_name': old_obj.dept_name,
		'dept_phone': old_obj.dept_mgr_phone, #????
		'contact': request.user.last_name + ',' + request.user.first_name, #????
		'dept_mgr': old_obj.dept_mgr
	}

	# Find all chartfields associated with selected department
	chartfield_list = (c['account_number'] for c in UmOscAcctsInUseV.objects.values('account_number').filter(deptid=select_dept))

	selected_cf = '50000-481054-10000-92320' #temp for testing

	#Get chartfield info for selected chartfield
	new_query = UmOscAcctsInUseV.objects.filter(account_number=selected_cf)
	obj = new_query[0]
	cf_info = {
		'cf': selected_cf,
		'shortcode': obj.short_code,
		'class_desc': obj.class_desc,
		'prgm_desc': obj.program_desc,
		'fund_desc': obj.fund_desc,
		'project_grant': obj.project_grant
	}

	# Find all user IDs currently assigned to a chartfield
	cf_users = (cf.user_defined_id for cf in UmOscAcctSubscribersV.objects.filter(chartcom=selected_cf).order_by('user_defined_id'))

	# Get user ID detail
	third_query = UmOscAcctSubscribersV.objects.filter(chartcom=selected_cf).order_by('user_defined_id')
	new_obj = third_query[len(third_query) - 1]
	user_info = {
		'id': new_obj.user_defined_id,
		'building': new_obj.building,
		'mrc': new_obj.mrc_charged,
		'toll': new_obj.toll_charged,
		'local': new_obj.local_charged
	}

	
	context = {
		'select_dept': default_dept,
		'deptids': user_depts,
		'dept_info': dept_info,
		'curr_chartfields': chartfield_list,
		'user_info': user_info,
		'users': cf_users,
		'test_template': 'test.html'
	}

	# Add entry to database
	# new_entry = UmOscAcctChangeInput(
	# 	uniqname=request.user.username,
	# 	user_defined_id=chosen_user,
	# 	mrc_acct_number=chosen_mrc,
	# 	toll_acct_number=chosen_toll,
	# 	local_acct_number=chosen_toll,
	# 	date_added=datetime.date)
	#new_entry.save()

	# Add record to Pinnacle
	#um_change_accts_by_subscrib_k.um_update_subscrib_from_web_p (username, datetime_added) where username=uniqname

	return HttpResponse(template.render(context, request))