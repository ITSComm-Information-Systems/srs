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

# from pinnmodels import UmOscAcctsInUseV
# from oscauth.models import AuthUserDept
# from reports.tolls.views import find_depts

def chartchange(request):
	template = loader.get_template('chartchange.html')

	# user_depts = AuthUserDept.objects.filter(user=request.user.id).order_by('dept').exclude(dept='All').distinct('dept')
	# chartfield_list = UmOscAcctsInUseV.objects.filter(deptid__in = user_depts)

	

	return HttpResponse(template.render({'title':'ChartField Change Request'}, request))


# def get_dept(request):
# 	if request.method =='POST':
# 		