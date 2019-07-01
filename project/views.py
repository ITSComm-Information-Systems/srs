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


@login_required
@permission_required(('oscauth.can_order','oscauth.can_report'), raise_exception=True)
def get_dept(request):
    if request.method == 'POST':
        dept_parm = request.POST['deptids']
        return HttpResponseRedirect('/chartchange/' + dept_parm + '/')


@login_required
@permission_required(('oscauth.can_order','oscauth.can_report'), raise_exception=True)
def change_dept(request, dept_parm):
	if request.method == "POST":
		change_dept = request.POST['select_dept']
		return HttpResponseRedirect(request.get_full_path() + 'to' + change_dept + '/')




@login_required
@permission_required(('oscauth.can_order','oscauth.can_report'), raise_exception=True)
def chartchange(request, dept_parm='', change_dept=''):
	template = loader.get_template('chartchange.html')
	
	# Find all departments user has access to
	user_depts = (d.dept for d in AuthUserDept.objects.filter(user=request.user.id).order_by('dept').exclude(dept='All').distinct('dept'))
	user_depts = list(user_depts)

	# Set selected department
	# if dept_parm == '':
	# 	select_dept = user_depts[0]
	# else:
	# 	select_dept = dept_parm
	# if select_dept not in user_depts:
	# 	template = loader.get_template('403.html')
	# 	return HttpResponse(template.render({'title':'uh oh'}, request))
	if request.GET.get('deptids') is None:
		select_dept = user_depts[0]
	else:
		select_dept = request.GET.get('deptids')

	# Get dept info from selected dept
	find_dept_info = UmOscDeptProfileV.objects.filter(deptid=select_dept)
	dept = find_dept_info[0]
	dept_info = {
		'dept_id': select_dept,
		'dept_name': dept.dept_name,
		'dept_mgr': dept.dept_mgr
	}

	# Find chartfields and details for selected department
	chartfield_list = UmOscAcctsInUseV.objects.filter(deptid=select_dept).order_by('account_number')

	# Determine selected chartfield
	if request.POST.get('chartcom') is None:
		if chartfield_list:
			selected_cf = chartfield_list[0]
		else:
			selected_cf = ''
	else:
		selected_cf = UmOscAcctsInUseV.objects.filter(account_number=request.POST.get('chartcom'))
		selected_cf = selected_cf[0]

	# Find chartfield nickname
	nickname = ''
	if selected_cf != '':
		nicknames = Chartcom.objects.all()
		for n in nicknames:
			if n.account_number == selected_cf:
				nickname = n.name


	# Find all User IDs currently assigned to a chartfield
	if selected_cf != '':
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
			if request.method == 'POST':
				user['selected'] = request.POST.get('select' + c.user_defined_id)
			users.append(user)
	else:
		users = ''

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
		'selected_users': users, #FIX 
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


@login_required
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
