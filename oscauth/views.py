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

from .models import AuthUserDept
from .models import Role, Group, User
from .forms import UserSuForm, AddUserForm
from .utils import su_login_callback, custom_login_action, upsert_user
from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV
from oscauth.forms import *


def get_name(request, parm=1):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            uniqname = form.cleaned_data['uniqname']
            upsert_user(uniqname)
            return HttpResponseRedirect('/auth/adduser?' + uniqname)

    else:
        if parm:
            result = 'User added'

        form = AddUserForm()
        context = {
            'result': result,
            'form': form,
            'title': 'Add User from MCommunity',
        }

    return render(request, 'oscauth/add_user.html', context)
 
def index(request):
    dept_list = AuthUserDept.objects.order_by('-id')
    template = loader.get_template('oscauth/manage_access.html')
    context = {
        'title': 'Manage User Access',
        'dept_list': dept_list,
    }
    return HttpResponse(template.render(context, request))

def dept(request, dept_id):
    dept_list = AuthUserDept.objects.order_by('-id')
    template = loader.get_template('oscauth/dept.html')
    context = {
        'title': 'Access for Department: ' + dept_id,
        'dept_list': dept_list,
    }
    return HttpResponse(template.render(context, request))

def user(request, user_id):
    roles = Role.objects.order_by('display_seq_no')
    template = loader.get_template('oscauth/user.html')
    context = {
        'title': 'Access for User: ' + user_id,
        'roles': roles
    }
    return HttpResponse(template.render(context, request))

def mypriv(request):
    depts = AuthUserDept.objects.filter(user=request.user.id).order_by('dept')
    rows = []
    prev_dept = ''
    dept_name = ''
    group_name = ''
    col1 = ''
    col2 = ''
    roles = ''
    i = 0
    for dept in depts:
        dept_info = UmOscDeptProfileV.objects.filter(deptid=dept.dept)
        print('Dept: %s' % dept.dept)
        if dept.dept == 'All':
            dept_name = 'All departments'
        else:
            for name in dept_info:
                dept_name = name.dept_name
        print('Name: %s' % name.dept_name)

        group_name = Group.objects.get(name=dept.group).name

        if dept.dept == prev_dept:
            roles = roles + ', ' + group_name
        else:
            if prev_dept != '':
                data = {'col1' : col1, 'col2' : col2,  'roles': roles}
                rows.append(data)
            i = i + 1
            col1 = dept.dept
            col2 = dept_name
            roles = group_name
        prev_dept = dept.dept
    data = {'col1' : col1, 'col2' : col2, 'roles': roles}
    rows.append(data)
    template = loader.get_template('oscauth/mypriv.html')
    context = {
        'title': 'My Privileges: ' + request.user.username,
        'rows': rows
    }
    return HttpResponse(template.render(context, request))


def get_dept(request):
    if request.method == 'POST':
        print(request.POST)
        print(request.POST.get('dept_parm'))
        print(request.POST[0])
        return HttpResponseRedirect('/auth/deptpriv/' + '481054' + '/')


def deptpriv(request, dept_parm):
    dept_list = UmCurrentDeptManagersV.objects.all().order_by('deptid')
    dept_info = UmCurrentDeptManagersV.objects.filter(deptid=dept_parm)
    users = AuthUserDept.objects.filter(dept=dept_parm).order_by('group','user__last_name','user__first_name')
    rows = []
    prev_user = ''
    group_name = ''
    col1 = ''
    col2 = ''
    roles = ''
    i = 0
    for dept in dept_info:
        deptid = dept.deptid
        dept_name = dept.dept_name
        dept_mgr_name = dept.dept_mgr_name
        dept_mgr_uniqname = dept.dept_mgr_uniqname

    for user in users:
        last_name = User.objects.get(username=user.user).last_name
        first_name = User.objects.get(username=user.user).first_name
        group_name = Group.objects.get(name=user.group).name
        if user.user == prev_user:
            roles = roles + ', ' + group_name
        else:
            if prev_user != '':
                data = {'col1' : col1, 'col2' : col2, 'roles': roles}
                rows.append(data)
            i = i + 1
            col1 = user.user
            col2 = last_name + ', ' + first_name
            roles = group_name
        prev_user = user.user
    data = {'col1' : col1, 'col2' : col2, 'roles': roles}
    rows.append(data)
    template = loader.get_template('oscauth/deptpriv.html')
    context = {
        'dept_list': dept_list,
        'subtitle1': 'Access For Department: ' + dept_parm + ' - '+ dept_name ,
        'subtitle2': 'Department Manager: ' + dept_mgr_name + ' (' + dept_mgr_uniqname + ')',
        'rows': rows
    }
    return HttpResponse(template.render(context, request))


#def setpriv(request):



@csrf_protect
@require_http_methods(['POST'])
@user_passes_test(su_login_callback)
def login_as_user(request, user_id):
    userobj = authenticate(request=request, su=True, user_id=user_id)
    if not userobj:
        raise Http404("User not found")

    exit_users_pk = request.session.get("exit_users_pk", default=[])
    exit_users_pk.append(
        (request.session[SESSION_KEY], request.session[BACKEND_SESSION_KEY]))

    maintain_last_login = hasattr(userobj, 'last_login')
    if maintain_last_login:
        last_login = userobj.last_login

    try:
        if not custom_login_action(request, userobj):
            login(request, userobj)
        request.session["exit_users_pk"] = exit_users_pk
    finally:
        if maintain_last_login:
            userobj.last_login = last_login
            userobj.save(update_fields=['last_login'])

    return HttpResponseRedirect('/')


@csrf_protect
@require_http_methods(['POST', 'GET'])
@user_passes_test(su_login_callback)
def su_login(request, form_class=UserSuForm, template_name='oscauth/su_login.html'):
    form = form_class(request.POST or None)
    user_list = User.objects.order_by('username')
    if form.is_valid():
        return login_as_user(request, form.get_user().pk)

    return render(request, template_name, {
        'title': 'Impersonate User',
        'form': form,
        'user_list': user_list,
    })


def su_logout(request):
    exit_users_pk = request.session.get("exit_users_pk", default=[])
    if not exit_users_pk:
        return HttpResponseBadRequest(
            ("This session was not su'ed into. Cannot exit."))

    user_id, backend = exit_users_pk.pop()

    userobj = get_object_or_404(get_user_model(), pk=user_id)
    userobj.backend = backend

    if not custom_login_action(request, userobj):
        login(request, userobj)
    request.session["exit_users_pk"] = exit_users_pk

    return HttpResponseRedirect(
        getattr(settings, "SU_LOGOUT_REDIRECT_URL", "/"))   



