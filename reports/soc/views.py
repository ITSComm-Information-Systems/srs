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
from oscauth.models import AuthUserDept, Grantor, Role

# from .models import AuthUserDept
# from .models import Role, Group, User
# from .forms import UserSuForm, AddUserForm
# from .utils import su_login_callback, custom_login_action, upsert_user
from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV
from oscauth.forms import *

def get_soc(request):
    template = loader.get_template('soc.html')
    depts = find_depts(request)
    groups = []
    query = UmOscDeptProfileV.objects.filter(deptid__in=depts).order_by('dept_grp').exclude(dept_grp='All')
    for q in query:
        groups.append(q.dept_grp)
    groups = list(dict.fromkeys(groups))
    context = {
        'title': 'Summary of Charges',
        'depts': depts,
        'groups': groups 
    }
    return HttpResponse(template.render(context,request))


def find_depts(request):
 	depts = []

 	query = AuthUserDept.objects.filter(user=request.user.id).order_by('dept').exclude(dept='All').distinct('dept')

 	for dept in query:
 		if Group.objects.get(name=dept.group).name != 'Orderer':
 			depts.append(dept.dept)

 	return depts

# def find_groups(request):
#     groups = []

#     query = UmOscDeptProfileV.objects.filter(deptid_

#     for group in query:
#         groups.append(group)
#     return groups