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

from project.pinnmodels import UmOscAcctsInUseV, UmOscAcctSubscribersV, UmOscDeptProfileV, UmOscAllActiveAcctNbrsV
from order.models import Chartcom
from oscauth.models import AuthUserDept
from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required

import json
from django.http import JsonResponse


#@login_required
@permission_required(('oscauth.can_order','oscauth.can_report'), raise_exception=True)
def get_dept(request):
    if request.method == 'POST':
        dept_parm = request.POST['deptids']
        return HttpResponseRedirect('/chartchange/' + dept_parm + '/')


#@login_required
@permission_required(('oscauth.can_order','oscauth.can_report'), raise_exception=True)
def chartchange(request, dept_parm='', change_dept=''):
	template = loader.get_template('chartchange.html')
	
	# Find all departments user has access to
	user_depts = (d.dept for d in AuthUserDept.objects.filter(user=request.user.id).order_by('dept').exclude(dept='All').distinct('dept'))
	user_depts = list(user_depts)


	# Set intitial department
	select_dept = user_depts[0]
	find_dept_info = UmOscDeptProfileV.objects.filter(deptid=select_dept)
	dept = find_dept_info[0]
	dept_info = {
		'dept_id': select_dept,
		'dept_name': dept.dept_name
	}

	# Set intitial chartfields
	chartfield_list = UmOscAcctsInUseV.objects.filter(deptid=select_dept).order_by('account_number')

	# Set intitial chartfield
	selected_cf = chartfield_list[0]

	# Find chartfield nickname
	nickname = ''
	if selected_cf != '':
		nicknames = Chartcom.objects.all()
		for n in nicknames:
			if n.account_number == selected_cf:
				nickname = n.name


	# Find all User IDs currently assigned to initial chartfield
	cf_users = UmOscAcctSubscribersV.objects.filter(chartcom=selected_cf.account_number).order_by('user_defined_id')
	users = []
	for c in cf_users:
		user = {
			'user_defined_id':c.user_defined_id,
			'building':c.building,
			'toll_charged':c.toll_charged,
			'mrc_charged':c.mrc_charged,
			'local_charged':c.local_charged,
			'selected': 'false'
		}
		users.append(user)

	# Select department to change to
	if change_dept == '':
		new_dept = user_depts[0]
	else:
		new_dept = change_dept
		if new_dept not in user_depts:
			template = loader.get_template('403.html')
			return HttpResponse(template.render({'title':'uh oh'}, request))
	new_cf = UmOscAllActiveAcctNbrsV.objects.filter(deptid=new_dept)

	
	context = {
		'deptids': user_depts,
		'dept_info': dept_info,
		'selected_cf': selected_cf,
		'cf_info': chartfield_list,
		'nickname': nickname,
		'users': users,
		'selected_users': '',
		'new_dept': new_dept,
		'new_cf': new_cf,
		'choose_cf_template': 'choose_cf.html',
		'choose_users_template': 'choose_users.html',
		'assign_new_template': 'assign_new.html',
		'review_submit_template': 'review_submit.html'
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


#@login_required
@permission_required(('oscauth.can_order','oscauth.can_report'), raise_exception=True)
def get_chartfield(request):
	template = loader.get_template('test.html')
	cf = request.POST.get('chartcom')
	selected_cf = UmOscAcctsInUseV.objects.filter(account_number=cf)
	context = {
		'selected_cf': selected_cf
	}
	return HttpResponse(template.render(context, request))


def get_table(request):
	selected_users = request.GET.get('selected', None)
	all_users = request.GET.get('all_users', None)





# Gives new chartfields when user changes department
def change_dept(request):
	selected_dept = request.GET.get('deptids', None)
	cf_options = list(UmOscAcctsInUseV.objects.filter(deptid=selected_dept).order_by('account_number').values())

	find_name = UmOscDeptProfileV.objects.filter(deptid=selected_dept)
	find_name = find_name[0]
	name = { 'name': find_name.dept_name }
	cf_options.append(name)

	return JsonResponse(cf_options, safe=False)


# Finds chartfield data when user changes chartfield
def get_cf_data(request):
	selected_cf = request.GET.get('selected', None)
	cf_data = list(UmOscAcctsInUseV.objects.filter(account_number=selected_cf).values())

	# Find chartfield nickname
	nickname = ''
	nicknames = Chartcom.objects.all()
	for n in nicknames:
		if n.account_number == selected_cf:
			nickname = n.name

	nn = {'nickname': nickname }
	cf_data.append(nn)

	return JsonResponse(cf_data, safe=False)


# Finds users for selected cahrtfield
def get_users(request):
	selected_cf = request.GET.get('selected', None)

	# Get info for selected chartfield
	cf = UmOscAcctsInUseV.objects.filter(account_number=selected_cf)
	cf = cf[0]

	# Find chartfield nickname
	nickname = ''
	if selected_cf != '':
		nicknames = Chartcom.objects.all()
		for n in nicknames:
			if n.account_number == selected_cf:
				nickname = n.name

	# Get users
	cf_users = UmOscAcctSubscribersV.objects.filter(chartcom=selected_cf).order_by('user_defined_id')
	users = []
	for c in cf_users:
		user = {
			'user_defined_id':c.user_defined_id,
			'building':c.building,
			'toll_charged':c.toll_charged,
			'mrc_charged':c.mrc_charged,
			'local_charged':c.local_charged,
			'selected': 'false'
		}
		if request.method == 'POST':
			user['selected'] = request.POST.get('select' + c.user_defined_id)
		users.append(user)


	context = {
		'selected_cf': cf,
		'nickname': nickname,
		'users': users
	}

	return render(request, 'choose_users.html', context)

