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
from project.pinnmodels import UmOscBillCycleV, UmOscDtDeptAcctListV, UmOscDeptProfileV
from oscauth.forms import *
from django.contrib.auth.decorators import login_required, permission_required

from datetime import datetime
from django.shortcuts import redirect

# Load intial Detail of Charge page
@permission_required('oscauth.can_report', raise_exception=True)
def get_new(request):
    template = loader.get_template('doc.html')

    # Find all departments user has access to
    user_depts = (d.dept for d in AuthUserDept.objects.filter(user=request.user.id).order_by('dept').exclude(dept='All').distinct('dept'))
    user_depts = list(user_depts)

    # Find dept names
    names = []
    name_query = list(d.dept_name for d in UmOscDeptProfileV.objects.filter(deptid__in=user_depts).order_by('deptid'))
    for i in range(0, len(user_depts)):
    	name = {
    		'deptid': user_depts[i],
    		'name': name_query[i]
    	}
    	names.append(name)

    # Find associated chartfields
    selected_dept = user_depts[0]
    dept_cfs = list((d.account_number for d in UmOscDtDeptAcctListV.objects.filter(deptid=selected_dept).order_by('account_number').distinct()))

    # Find all available billing dates
    billing_dates = list((d.billing_date for d in UmOscBillCycleV.objects.all().order_by('billing_date').reverse()))

    context = {
        'title': 'New Report',
        'form_action': '/reports/new/report/nontelephony/',
        'names': names,
        'dates': billing_dates,
        'initial_date':billing_dates[0],
        'dept_cfs': dept_cfs
    }
    return HttpResponse(template.render(context,request))