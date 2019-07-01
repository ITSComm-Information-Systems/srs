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
from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV
from oscauth.forms import *
from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required('oscauth.can_report', raise_exception=True)
def get_doc(request):
    template = loader.get_template('doc.html')

    # Find all departments user has access to
    user_depts = (d.dept for d in AuthUserDept.objects.filter(user=request.user.id).order_by('dept').exclude(dept='All').distinct('dept'))
    user_depts = list(user_depts)

    context = {
        'title': 'Detail of Charges',
        'user_depts': user_depts,
        'dates': {'not', 'found', 'yet'}, #um_osc_bill_cycle_v
        'dept_cfs': {'Just', 'trying', 'to', 'do', 'front', 'end'}
    }
    return HttpResponse(template.render(context,request))



def generate_report(request):
	template = loader.get_template('doc-report.html')

	context= {
		'title':'Detail of Charges'
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