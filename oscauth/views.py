import warnings

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.template import loader
from django.db import models
from django.db.utils import IntegrityError
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login, logout, authenticate, user_logged_in
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_http_methods
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django import forms

from ldap3 import Server, Connection, ALL

#from .models import AuthUserDept
from .models import AuthUserDept, Grantor, Role, Group, User
from .forms import UserSuForm, AddUserForm
from .utils import su_login_callback, custom_login_action, upsert_user
from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV
from oscauth.forms import *
from oscauth.utils import upsert_user
#from oscauth.models import AuthUserDept, Grantor, Role


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
        context = {
            'title' : 'Department Look Up',
            'dept_list': dept_list
        }
        return  HttpResponse(template.render(context, request))

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
        'title' : 'Department Look Up',
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
        uniqname_parm = request.POST['uniqname_parm']


    if uniqname_parm == '':
        set_priv = ''
        return  HttpResponse(template.render({'uniqname_parm': uniqname_parm, 'title':"Manage Access"}, request))
    else:
        # Check for valid uniqname format
        if len(uniqname_parm) < 3 or len(uniqname_parm) > 8 or uniqname_parm.isalpha is False:
            result = uniqname_parm + ' is not a valid uniqname'
            return  HttpResponse(template.render({'result': result, 'title':"Manage Access"}, request))
        else:
            # Get User from MCommunity
            conn = Connection('ldap.umich.edu', auto_bind=True)
            conn.search('ou=People,dc=umich,dc=edu', '(uid=' + uniqname_parm + ')', attributes=["uid","mail","user","givenName","sn"])
            
            if conn.entries:
                mc_user = conn.entries[0]
                result = ''

                try:
                    osc_user = User.objects.filter(username=uniqname_parm)
                except:
                    osc_user = User()

                if osc_user:
                    osc_user.exists = True

                osc_user.username = mc_user.uid
#                osc_user.last_name = mc_user.sn
#                osc_user.first_name = mc_user.givenName
                last_name = mc_user.sn
                first_name = mc_user.givenName

                if(request.user.has_perm('oscauth.can_administer_access_all')):
                    grantable_roles = Role.objects.filter(grantable_by_dept=True,active=True).order_by('role')
                    dept_manager = AuthUserDept.objects.filter(user=request.user.id,group=3)
                else:
                    grantable_roles = Role.objects.filter(grantable_by_dept=True,active=True).exclude(role='Proxy').order_by('role')
                    dept_manager = []

                print(dept_manager)
                #grantable_roles = Role.objects.filter(grantable_by_dept=True,active=True).order_by('role')
                grantor_roles = Grantor.objects.values('grantor_role').distinct()
                this_grantors_roles = AuthUserDept.objects.filter(user=request.user.id).values("group").distinct()
# The list of roles should only include those that this particular user can grant
#                grantable_roles = Grantor.objects.filter(grantor_role__in=this_grantors_roles).values("granted_role_id").distinct()

# The list of depts should be dependent on the role selected
#   e.g. if proxy is selected, only those depts for which thia grantor has the dept manager role should be displayed
                grantor_depts = AuthUserDept.objects.filter(user=request.user.id,group__in=grantor_roles).exclude(dept='All').order_by('dept')

                rows = []
                dept_name = ''
                dept_status = ''
                process_access = ''
                submit_msg = ''

                for role in grantable_roles:
                    role = role.role
#                    role = grantable_roles.granted_role_id
#                    role = Role.objects.get(id=granted_role_id).role

                for dept in grantor_depts:
                    dept = dept.dept

                    if dept_manager.filter(dept=dept).exists():
                    #if dept in dept_manager:
                        manager = True
                    else:
                        manager = False

                    dept_info = UmCurrentDeptManagersV.objects.get(deptid=dept)
                    dept_name = dept_info.dept_name
                    dept_status = dept_info.dept_status
                    data = {'dept_status' : dept_status,'dept' : dept, 'dept_name' : dept_name, 'dept_manager': manager}
                    rows.append(data)

                context = {
                    'title':"Manage Access",
                    'uniqname_parm': uniqname_parm,
                    'osc_user': osc_user,
                    'last_name': last_name,
                    'first_name': first_name,
                    'grantor_depts': grantor_depts,
                    'grantable_roles': grantable_roles,
                    'dept_name': dept_name,
                    'rows': rows,
                    'result': result,
                    'submit_msg': submit_msg,
                }

                if request.method=='POST' and request.POST.get('process_access'):
                    if request.POST.get('rolerad') and request.POST.get('deptck'):
                        submit_msg = 'Ready to Process'
                        if request.POST.get('taskrad') == 'add':
#                            return render(request,'oscauth/addpriv.html', context)
                            return HttpResponseRedirect('/auth/addpriv/' + uniqname_parm, context, 'not') # do I need to pass in the page title here?
                        if request.POST.get('taskrad') == 'remove':
                            return render(request, 'oscauth/removepriv.html', context) # do I need to pass in the page title here?

                    else:
                        submit_msg = 'Please select a Task, a Role, and at least one Department then click Submit.'
                        return  HttpResponse(template.render({'submit_msg': submit_msg, 'title':"Manage Access"}, request)) # do I need to pass in the page title here?

                return render(request, 'oscauth/setpriv.html', context)

            else:
                result = uniqname_parm + ' is not in MCommunity'
                return  HttpResponse(template.render({'result': result, 'title':"Manage Access"}, request))


def showpriv(request, uniqname_parm):

    template = loader.get_template('oscauth/showpriv.html')
    if uniqname_parm == '':
        result = 'Please enter uniqname'
        return HttpResponseRedirect('/auth/setpriv/', request)

    else:
        try:
            osc_user = User.objects.get(username=uniqname_parm)
            user_id = osc_user.id

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
                'title': 'Current Privileges for: ' + osc_user.last_name + ', ' + osc_user.first_name + ' (' + uniqname_parm + ')',
                'rows': rows
            }
        except:
            raise Http404

    return HttpResponse(template.render(context, request))


def modpriv(request):

    if request.method == 'POST':
            uniqname_parm = request.POST['uniqname_parm']
            last_name = request.POST['last_name']
            first_name = request.POST['first_name']
            action_checked = request.POST['taskrad']
            dept_checked = request.POST.getlist('deptck')

    try:
        osc_user = User.objects.get(username=uniqname_parm)
        result = 'User already exists'
    except:
        osc_user = upsert_user(uniqname_parm) 
        result = 'Added user'

    if action_checked == 'add':
        add_checked = request.POST['roleAdd']
        role_checked = add_checked
        for dept in dept_checked:
            new_auth = AuthUserDept()
            new_auth.user = osc_user
            new_auth.group = Role.objects.get(role=add_checked).group
            new_auth.dept = dept

            try:
                new_auth.save()
                result = 'Privilege Added'
            except IntegrityError: 
                result = 'Privilege already exists'
            
    else:
        del_checked = request.POST.getlist('roleDelete')
        role_checked = del_checked
        for del_role in del_checked:
            role = Role.objects.get(role=del_role).group
            aud = AuthUserDept.objects.filter(user=osc_user,group=role,dept__in=dept_checked)
            aud.delete()
            result = 'Deleted Privileges'

    context = {
        'title': "Manage Access",
        'subtitle': 'Adding privileges for: ' + last_name + ', ' + first_name + ' (' + uniqname_parm + ')',
        'uniqname_parm': uniqname_parm,
        'last_name': last_name,
        'first_name': first_name,
        'role_checked': role_checked,
        'dept_checked': dept_checked,
        'result': result
    }

    return render(request,'oscauth/modpriv.html', context)


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

    add_custom_permissions(user_id)

    return HttpResponseRedirect('/')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def add_custom_permissions(user_id):
    # Add permissions for groups the user is in.  

    groups = AuthUserDept.objects.filter(user=user_id).distinct('group_id')
    u = User.objects.get(id=user_id)

    for group in groups:
        g = Group.objects.get(id=group.group_id)
        for perm in g.permissions.all():
            u.user_permissions.add(perm)


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

def chart_change(request):
    template = loader.get_template('oscauth/chartchange.html');

    return HttpResponse(template.render({'title':'Chartfield Change Request'}, request))

