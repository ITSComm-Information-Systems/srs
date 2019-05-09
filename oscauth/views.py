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
    dept_status = ''
    group_name = ''
    col1 = ''
    col2 = ''
    roles = ''
    i = 0
    for dept in depts:
        dept_info = UmOscDeptProfileV.objects.filter(deptid=dept.dept)
        if dept.dept == 'All':
            dept_name = 'All departments'
            dept_status = 'A'
        else:
            for name in dept_info:
                dept_name = name.dept_name

        group_name = Group.objects.get(name=dept.group).name

        if dept.dept == prev_dept:
            roles = roles + ', ' + group_name
        else:
            if prev_dept != '':
                data = {'dept_status' : dept_status,'col1' : col1, 'col2' : col2,  'roles': roles}
                rows.append(data)
            i = i + 1
            dept_status = name.dept_eff_status
            col1 = dept.dept
            col2 = dept_name
            roles = group_name
        prev_dept = dept.dept
    data = {'dept_status' : dept_status,'col1' : col1, 'col2' : col2, 'roles': roles}
    rows.append(data)
    template = loader.get_template('oscauth/mypriv.html')
    context = {
        'title': 'My Privileges: ' + request.user.username,
        'rows': rows
    }
    return HttpResponse(template.render(context, request))


def get_dept(request):
    if request.method == 'POST':
        dept_parm = request.POST['dept_parm']
        return HttpResponseRedirect('/auth/deptpriv/' + dept_parm + '/')
    else:
        dept_priv = ''


def deptpriv(request, dept_parm=''):
    template = loader.get_template('oscauth/deptpriv.html')
    dept_list = UmCurrentDeptManagersV.objects.all().order_by('deptid')
    if dept_parm == '':
        return  HttpResponse(template.render({'dept_list': dept_list},request))

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
        dept_status = dept.dept_status
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
    context = {
        'dept_list': dept_list,
        'dept_status': dept_status,
        'subtitle1': 'Access For Department: ' + dept_parm + ' - '+ dept_name ,
        'subtitle2': 'Department Manager: ' + dept_mgr_name + ' (' + dept_mgr_uniqname + ')',
        'rows': rows
    }
    return HttpResponse(template.render(context, request))


def get_uniqname(request, uniqname_parm=''):
    template = loader.get_template('oscauth/setpriv.html')
    if request.method == 'POST':  #big work here
        print(request.POST)
        uniqname_parm = request.POST['uniqname_parm']
#        process_access = request.POST['process_access']


    if uniqname_parm == '':
        set_priv = ''
        return  HttpResponse(template.render({'uniqname_parm': uniqname_parm}, request))
    else:
        # Check for valid uniqname format
        if len(uniqname_parm) < 3 or len(uniqname_parm) > 8 or uniqname_parm.isalpha is False:
            result = uniqname_parm + ' is not a valid uniqname'
            print('uniqname_parm: %s %s' % (uniqname_parm, result))
            return  HttpResponse(template.render({'result': result}, request))
        else:
            # Get User from MCommunity
            conn = Connection('ldap.umich.edu', auto_bind=True)
            conn.search('ou=People,dc=umich,dc=edu', '(uid=' + uniqname_parm + ')', attributes=["uid","mail","user","givenName","sn"])
            
            if conn.entries:
                mc_user = conn.entries[0]
                result = ''

                try:
                    osc_user = User.objects.filter(username=uniqname_oarm)
                except:
                    osc_user = User()

                osc_user.username = mc_user.uid
                osc_user.last_name = mc_user.sn
                osc_user.first_name = mc_user.givenName
                osc_user.email = mc_user.mail

                print('Uniqname: %s   Last Name: %s   First Name: %s' % (uniqname_parm, osc_user.last_name, osc_user.first_name))

                TASK_CHOICES = [
                    ('Add','Add Access'),
                    ('Remove','Remove Access'),
                ]

#                task = models.CharField(max_length=15, choices=TASK_CHOICES)
#                tasks = forms.ChoiceField(choices=TASK_CHOICES, widget=forms.RadioSelect)
                tasks = forms.ChoiceField(choices=TASK_CHOICES)


                grantor_depts = AuthUserDept.objects.filter(user=request.user.id).exclude(dept='All').order_by('dept')
                grantable_roles = Role.objects.filter(grantable_by_dept=True,active=True).order_by('role')
                rows = []
                dept_name = ''
                dept_status = ''
                process_access = ''
                submit_msg = ''

                for role in grantable_roles:
                    role = role.role

                for dept in grantor_depts:
                    dept = dept.dept
                    dept_info = UmCurrentDeptManagersV.objects.get(deptid=dept)
                    dept_name = dept_info.dept_name
                    dept_status = dept_info.dept_status
                    data = {'dept_status' : dept_status,'dept' : dept, 'dept_name' : dept_name}
                    rows.append(data)

                print('Dept status: %s  Dept Name: %s' % (dept_status, dept_name))


                context = {
                    'uniqname_parm': uniqname_parm,
#                    'osc_user': osc_user,
#                    'osc_user.last_name': osc_user.last_name,
#                    'osc_user.first_name': osc_user.first_name,
                    'last_name': osc_user.last_name,
                    'first_name': osc_user.first_name,
                    'grantor_depts': grantor_depts,
                    'grantable_roles': grantable_roles,
                    'dept_name': dept_name,
                    'tasks': tasks,
                    'rows': rows,
                    'result': result,
                    'process_access': process_access,
                    'submit_msg': submit_msg,
                }

                print(request.POST.get('process_access'))

                if request.method=='POST': # and request.POST.get('process_access'):
                    print('Submitted')
                    if 'rolerad' and 'deptck':
                        submit_msg = 'Ready to Process'
                        print('Ready to Process')
                    else:
                        submit_msg = 'Please select a Task, a Role, and at least one Department then click Submit.'
                        print('Incomplete input')
                

                return render(request, 'oscauth/setpriv.html', context)
                #return HttpResponseRedirect('/auth/setpriv/' + uniqname_parm + '/' + last_name + '/' + first_name + '/')

            else:
                result = uniqname_parm + ' is not in MCommunity'
                return  HttpResponse(template.render({'result': result}, request))



def setpriv(request, uniqname_parm, last_name, first_name):
#    result  = ''
#    last_name = ''
#    first_name = ''

    template = loader.get_template('oscauth/setpriv.html')
#    if request.method == 'POST':
#        uniqname_parm = request.POST['uniqname_parm']
#        osc_user = request.POST['osc_user']
#        last_name = request.POST['last_name']
#        first_name = request.POST['first_name']
#        print('osc_user: %s' % osc_user)
#        last_name = osc_user.last_name
#        first_name = osc_user.first_name

#    if uniqname_parm == '':
#        return  HttpResponse(template.render(request))

    if uniqname_parm is not None:
        print('Uniqname: %s   Last Name: %s   First Name: %s' % (uniqname_parm, last_name, first_name))

    grantor_depts = AuthUserDept.objects.filter(user=request.user.id).exclude(dept='All').order_by('dept')
    len()
    print('User: ' + request.user.id)
    print('Grantor_depts: ' + grantor_depts)
    grantable_roles = Role.objects.filter(grantable_by_dept=True,active=True).order_by('role')
    rows = []
    dept_name = ''
    dept_status = ''

    for role in grantable_roles:
        role = role.role

    for dept in grantor_depts:
        dept = dept.dept
        dept_info = UmCurrentDeptManagersV.objects.get(deptid=dept)
        dept_name = dept_info.dept_name
        dept_status = dept_info.dept_status
        data = {'dept_status' : dept_status,'dept' : dept, 'dept_name' : dept_name}
        rows.append(data)

    dept_checked = request.POST.getlist('dchcecks[]')
    role_checked = request.POST.getlist('rchcecks[]')

    print(dept_checked)
    print(role_checked)


    context = {
        'uniqname_parm': uniqname_parm,
        'last_name': last_name,
        'last_name': last_name,
        'dept_checked': dept_checked,
        'role_checked': dept_checked,
        'grantable_roles': grantable_roles,
        'grantor_depts': grantor_depts,
        'rows': rows
    }
    return HttpResponse(template.render(context, request))


def showpriv(request, uniqname_parm, last_name, first_name):
    user_id = ''

    if request.method == 'POST':
        uniqname_parm = request.POST['uniqname_parm']
        last_name = request.POST['last_name']
        first_name = request.POST['first_name']

    template = loader.get_template('oscauth/showpriv.html')
    if uniqname_parm == '':
        result = 'Please enter uniqname'
        return HttpResponseRedirect('/auth/setpriv/', request)

    else:

        try:
            user_id = User.objects.get(username=uniqname_parm).id
    #        depts = AuthUserDept.objects.filter(user=osc_user.id).order_by('dept')
            depts = AuthUserDept.objects.filter(user=user_id).order_by('dept')
            rows = []
            prev_dept = ''
            dept_name = ''
            dept_status = ''
            group_name = ''
            col1 = ''
            col2 = ''
            roles = ''
            i = 0
            for dept in depts:
    #            template = loader.get_template('oscauth/showpriv.html')
                dept_info = UmOscDeptProfileV.objects.filter(deptid=dept.dept)
                if dept.dept == 'All':
                    dept_name = 'All departments'
                    dept_status = 'A'
                else:
                    for name in dept_info:
                        dept_name = name.dept_name

                group_name = Group.objects.get(name=dept.group).name

                if dept.dept == prev_dept:
                    roles = roles + ', ' + group_name
                else:
                    if prev_dept != '':
                        data = {'dept_status' : dept_status,'col1' : col1, 'col2' : col2,  'roles': roles}
                        rows.append(data)
                    i = i + 1
                    dept_status = name.dept_eff_status
                    col1 = dept.dept
                    col2 = dept_name
                    roles = group_name
                prev_dept = dept.dept
            data = {'dept_status' : dept_status,'col1' : col1, 'col2' : col2, 'roles': roles}
            rows.append(data)
        #    template = loader.get_template('oscauth/showpriv.html')
            context = {
                'title': 'Current Privileges for: ' + last_name + ', ' + first_name + ' (' + uniqname_parm + ')',
                'rows': rows
            }
        except:
            context = {
                'title': 'There currently are no privileges for: ' + last_name + ', ' + first_name + ' (' + uniqname_parm + ')'
            }
            
    return HttpResponse(template.render(context, request))


def addpriv(request, uniqname_parm):
#def addpriv(request):
    result = ''
    template = loader.get_template('oscauth/addpriv.html')

    if request.method == 'POST':
        uniqname_parm = request.POST['uniqname_parm']
        osc_user = request.POST['osc_user']
        last_name = request.POST['last_name']
        first_name = request.POST['first_name']
        dept_checked = request.POST['dept_checked']
        role_checked = request.POST['role_checked']
        result = request.POST['result']
        print('Add access for %s' % uniqname_parm)

    try:
        user_id = User.objects.get(username=uniqname_parm).id
        result = 'User already exists'
        print('User already exists')
    except:
#    	upsert_user(uniqname_parm)
        result = 'Added user'
        print('Added user')
        user_id = User.objects.get(username=uniqname_parm).id

        new_auth = AuthUserDept()

#    for dept in dept_checked:
#	    for role in role_checked:
#            groupid = Role.objects.get(role=role.rchecked).group

#            new_auth.user = user_id
#            new_auth.role = groupid
#            new_auth.dept = dept.deptid
#            new_auth.save()

#            result = 'Added'
#            print('Added User: %s  Role: %s   Dept: %s' % (uniqname_parm, new_auth.role, new_auth.dept))

#        context = {
#            'title': 'Adding privileges for: ' + last_name + ', ' + first_name + ' (' + uniqname_parm + ')',
#            'uniqname_parm': uniqname_parm,
#            'last_name': last_name,
#            'first_name': first_name,
#            'result': result
#        }

#    return HttpResponseRedirect('/auth/setpriv/' + uniqname_parm + '/', context)
        return HttpResponse(template.render(context, request))



def removepriv(request, uniqname_parm):
#def removepriv(request):
    result = ''
    template = loader.get_template('oscauth/addpriv.html')

    if request.method == 'POST':
        uniqname_parm = request.POST['uniqname_parm']
        osc_user = request.POST['osc_user']
        last_name = request.POST['last_name']
        first_name = request.POST['first_name']
        dept_checked = request.POST['dept_checked']
        role_checked = request.POST['role_checked']
        result = request.POST['result']
        print('Remove access for %s' % uniqname_parm)

        user_id = User.objects.get(username=uniqname_parm).id

    for dept in dept_checked:
	    for role in role_checked:
		    groupid = Role.objects.get(role=role.rchecked).group


		    try:
			    osc_auth = AuthUserDept.objects.filter(user=user_id, dept=dept.deptid, role=groupid)
#			    osc_auth.delete()

			    print('Removed User: %s  Role: %d   Dept: %s' % (uniqname_parm, role.role, dept.deptid))

		    except:   
			    continue

    context = {
        'uniqname_parm': uniqname_parm,
        'osc_user': osc_user,
        'result': result,
    }
#    return HttpResponseRedirect('/auth/setpriv/' + uniqname_parm + '/', context)
    return HttpResponse(template.render(context, request))



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



