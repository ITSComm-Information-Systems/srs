import warnings

from django.contrib.auth.decorators import permission_required
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
from project.pinnmodels import UmOscDeptProfileV, UmCurrentDeptManagersV, UmOscAcctSubscribersV,UmOscServiceProfileV,UmOscAuthUsersApi
from oscauth.forms import *
from oscauth.utils import upsert_user, get_mc_user
from pages.models import Page
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
        'title': "View My System Privileges",
        'subtitle': 'My Privileges: ' + request.user.username,
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
        uniqname_parm = request.POST['uniqname_parm'].lower()

    # Initial page - no uniqname provided yet
    if uniqname_parm == '':
        set_priv = ''
        return  HttpResponse(template.render({'uniqname_parm': uniqname_parm, 'title':"Manage User Access"}, request))
    # Load permissions
    else:
        # Account for incorrectly formatted uniqnames
        if len(uniqname_parm) < 3 or len(uniqname_parm) > 8 or uniqname_parm.isalpha is False:
            result = uniqname_parm + ' is not a valid uniqname'
            return  HttpResponse(template.render({'result': result, 'title':"Manage User Access"}, request))
        # User tries to manage own access
        elif uniqname_parm == request.user.username:
            result = 'You are attempting to view your own access. '
            osc_user = {
                'exists': True
            }
            return  HttpResponse(template.render({'result': result, 'osc_user': osc_user, 'title':"Manage User Access"}, request))
        else:
            # Get User from MCommunity
            #conn = Connection('ldap.umich.edu', auto_bind=True)
            #conn.search('ou=People,dc=umich,dc=edu', '(uid=' + uniqname_parm + ')', attributes=["uid","mail","user","givenName","sn"])
            
            mc_user = get_mc_user(uniqname_parm)

            # User exists in MCommunity
            if mc_user:
            #if conn.entries:
                #mc_user = conn.entries[0]
                result = uniqname_parm

                try:
                    osc_user = User.objects.filter(username=uniqname_parm)
                except:
                    osc_user = User()

                if osc_user:
                    osc_user.exists = True

                osc_user.username = mc_user.uid
                last_name = mc_user.umichDisplaySn 
                first_name = mc_user.givenName

                if(request.user.has_perm('oscauth.can_administer_access_all')):
                    grantable_roles = Role.objects.filter(grantable_by_dept=True,active=True).order_by('role')
                    dept_manager = AuthUserDept.objects.filter(user=request.user.id,group=3)
                    disable_proxy = False
                else:
                    grantable_roles = Role.objects.filter(grantable_by_dept=True,active=True).exclude(role='Proxy').order_by('role')
                    dept_manager = []
                    disable_proxy = True

                #grantable_roles = Role.objects.filter(grantable_by_dept=True,active=True).order_by('role')
                grantor_roles = Grantor.objects.values('grantor_role').distinct()
                #this_grantors_roles = AuthUserDept.objects.filter(user=request.user.id).values("group").distinct()
                # # The list of roles should only include those that this particular user can grant
                # #grantable_roles = Grantor.objects.filter(grantor_role__in=this_grantors_roles).values("granted_role_id").distinct()

                # # The list of depts should be dependent on the role selected
                # #   e.g. if proxy is selected, only those depts for which thia grantor has the dept manager role should be displayed
                grantor_depts = AuthUserDept.objects.filter(user=request.user.id,group__in=grantor_roles).exclude(dept='All').order_by('dept')

                rows = []
                dept_name = ''
                dept_status = ''
                process_access = ''
                submit_msg = ''

                for role in grantable_roles:
                    role = role.role
                    #role = grantable_roles.granted_role_id
                    #role = Role.objects.get(id=granted_role_id).role

                for query_dept in grantor_depts:
                    dept = query_dept.dept

                    if dept_manager and dept_manager.filter(dept=dept).exists():
                    #if dept in dept_manager:
                        manager = True
                    else:
                        manager = False

                    dept_info = UmCurrentDeptManagersV.objects.get(deptid=dept)
                    dept_name = dept_info.dept_name
                    dept_status = dept_info.dept_status

                    # Determine selected user's roles for system user's departments
                    roles = {
                        'proxy': False,
                        'orderer': False,
                        'reporter': False
                    }
                    user_roles = []
                    if osc_user:
                        roles_list = AuthUserDept.objects.filter(user=osc_user[0], dept=dept)
                        user_roles = []
                        for role in roles_list:
                            user_roles.append(role.group.role.role)

                        # Create for checkboxes
                        proxy = False
                        orderer = False
                        reporter = False
                        if 'Proxy' in user_roles:
                            proxy = True
                        if 'Orderer' in user_roles:
                            orderer = True
                        if 'Reporter' in user_roles:
                            reporter = True
                        roles = {
                            'proxy': proxy,
                            'orderer': orderer,
                            'reporter': reporter
                        }

                    # Get the requestor's role for that department
                    role = query_dept.group.role.role

                    disable_proxy = False
                    disable_others = False
                    if role != "Proxy" and role != 'Department Manager':
                        disable_others = True
                        disable_proxy = True

                    data = {
                        'dept_status' : dept_status,
                        'dept' : dept, 
                        'dept_name' : dept_name, 
                        'dept_status': dept_status,
                        'dept_manager': manager,
                        'disable_proxy': disable_proxy,
                        'disable_others': disable_others,
                        'my_role': role,
                        'current_roles': roles,
                        'roles_list': ", ".join(user_roles)
                    }
                    rows.append(data)

                # Get permission information
                information = Page.objects.get(permalink='/manageacces')


                context = {
                    'title':"Manage User Access",
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
                    'information': information,
                    'disable_proxy': disable_proxy
                }

                return render(request, 'oscauth/setpriv.html', context)

            # If user does not exist in MCommunity
            else:
                result = uniqname_parm + ' is not in MCommunity'
                return  HttpResponse(template.render({'result': result, 'title':"Manage User Access"}, request))


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

        # action_checked = request.POST['taskrad']
        dept_list = request.POST.getlist('dept_list')

        # Get department info
        dept_info = UmCurrentDeptManagersV.objects.filter(deptid__in = dept_list)

    # Add user if needed
    try:
        osc_user = User.objects.get(username=uniqname_parm)
        result = 'User already exists'
    except:
        osc_user = upsert_user(uniqname_parm) 
        result = 'Added user'

    modifications = {}

    for dept in dept_list:
        modifications[dept] = {
            'added': [],
            'deleted': [],
            'inactive': False,
            'name': ''
        }
        # Add/delete proxy status
        proxy_actions = request.POST.get(dept + 'proxy')
        if proxy_actions == 'add':
            result = add_priv(osc_user, 'Proxy', dept)
            if result == 'change':
                modifications[dept]['added'].append('Proxy')

        elif proxy_actions == 'delete':
            result = delete_priv(osc_user, 'Proxy', dept)
            if result == 'change':
                modifications[dept]['deleted'].append('Proxy')

        # Add/delete orderer status
        orderer_actions = request.POST.get(dept + 'orderer')
        if orderer_actions == 'add':
            result = add_priv(osc_user, 'Orderer', dept)
            if result == 'change':
                modifications[dept]['added'].append('Orderer')

        elif orderer_actions == 'delete':
            result = delete_priv(osc_user, 'Orderer', dept)
            if result == 'change':
                modifications[dept]['deleted'].append('Orderer')

        # Add/delete reporter status
        reporter_actions = request.POST.get(dept + 'reporter')
        if reporter_actions == 'add':
            result = add_priv(osc_user, 'Reporter', dept)
            if result == 'change':
                modifications[dept]['added'].append('Reporter')

        elif reporter_actions == 'delete':
            result = delete_priv(osc_user, 'Reporter', dept)
            if result == 'change':
                modifications[dept]['deleted'].append('Reporter')

    # Department inactive vs. active and name
    for info in dept_info:
        if info.dept_status == 'I':
            modifications[info.deptid]['inactive'] = True
        modifications[info.deptid]['name'] = info.dept_name


    context = {
        'title': "Manage User Access",
        'subtitle': 'Adding privileges for: ' + last_name + ', ' + first_name + ' (' + uniqname_parm + ')',
        'uniqname_parm': uniqname_parm,
        'last_name': last_name,
        'first_name': first_name,
        'modifications': modifications
    }

    return render(request,'oscauth/modpriv.html', context)


@csrf_protect
@require_http_methods(['POST'])
#@user_passes_test(su_login_callback)
@permission_required('oscauth.can_impersonate')
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

    groups = AuthUserDept.objects.filter(user=user_id).distinct().values('group_id')
    u = User.objects.get(id=user_id)

    for group in groups:
        g = Group.objects.get(id=group.get('group_id'))
        for perm in g.permissions.all():
            u.user_permissions.add(perm)


@csrf_protect
@require_http_methods(['POST', 'GET'])
#@user_passes_test(su_login_callback)
@permission_required('oscauth.can_impersonate')
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

def add_priv(osc_user, role, dept):
    new_auth = AuthUserDept()
    new_auth.user = osc_user
    new_auth.group = Role.objects.get(role=role).group
    new_auth.dept = dept

    try:
        new_auth.save()
        result = 'change'
    except IntegrityError: 
        result = 'no change'

    try:
        rec = UmOscAuthUsersApi()
        rec.dept = dept
        rec.group_name = new_auth.group.name
        rec.username = osc_user.username
        rec.save()
    except:
        print('error updating UmOscAuthUsersApi')

    return result

def delete_priv(osc_user, role, dept):
    role = Role.objects.get(role=role).group
    aud = AuthUserDept.objects.filter(user=osc_user,group=role,dept=dept)

    try:
        UmOscAuthUsersApi.objects.filter(username=osc_user.username,group_name=role.name,dept=dept).delete()
    except:
        print('error delete from UmOscAuthUsersApi')

    result = 'no change'
    if aud.exists():
        aud.delete()
        result = 'change'

    return result

def userid(request):
    template = loader.get_template('oscauth/userid.html')
    
    user_param=''
    rows = []
    user_list=[]

    if request.method=='POST':
        user_param = request.POST.get('user_param').strip()
        user_param = ''.join(char for char in user_param if char.isalnum())

    if user_param == '':
        context = {
            'title' : 'User ID Look Up',
            'user_list': 'blank'
        }
        return  HttpResponse(template.render(context, request))
    
    if (len(user_param)==16) or (len(user_param)==10):
        user_list= UmOscAcctSubscribersV.objects.filter(user_defined_id__contains=user_param)

    
    for user in user_list:
        user_def_id = user.user_defined_id
        chartcom_data = user.chartcom.split('-')
        fund=chartcom_data[0]
        deptid=chartcom_data[1]
        program=chartcom_data[2]
        chartcom_class=chartcom_data[3]

        building = user.building
        floor = user.floor
        room = user.room
        jack = user.jack

        yn={'Y':'Yes','N':'No'}
        mrc = yn[user.mrc_charged]
        toll = yn[user.toll_charged]
        local = yn[user.local_charged]
        
        deptid_list=set()
        for x in UmOscServiceProfileV.objects.filter(user_defined_id=user_def_id, service_status_code="In Service", subscriber_status="Active"):
            deptid_list.add(x.deptid)

        #get manager information from the department id if any
        for deptid in deptid_list:
            uniqname = AuthUserDept.objects.get(dept=deptid, group = 3).user.username
            firstname=AuthUserDept.objects.get(dept=deptid, group = 3).user.first_name
            lastname=AuthUserDept.objects.get(dept=deptid, group = 3).user.last_name

            manager= lastname+', '+firstname+" ("+uniqname+")"

            data = {'user_def_id' : user_def_id, 'manager':manager, 'fund': fund, 'deptid':deptid, 'program':program, 'chartcom_class':chartcom_class, 'building' : building, 'floor': floor, 'room': room, 'jack': jack, 'mrc': mrc, 'toll': toll, 'local': local}

            for info in data.items():
                if info[1]=='':
                    data[info[0]]='None'
            rows.append(data)

    
    context = {
        'title' : 'User ID Look Up',
        'subtitle1': 'Results for: ' + user_param ,
        'rows': rows,
        'user_list':user_list,
    }
    return HttpResponse(template.render(context, request))

from django import template

register = template.Library()


def numberlookup(request):
    if request.method == 'GET':
        return render(request, 'oscauth/numberlookup.html', {'title': 'Number Look Up'})

    elif request.method == 'POST':
        user_param = request.POST.get('user_param', '') 
        logged_in_user = request.user
        try:
            osc_user = User.objects.get(username=user_param)
        except User.DoesNotExist:
            return HttpResponse('<div>User not found</div>')
        
        dept_list = AuthUserDept.objects.filter(user=logged_in_user).values_list('dept', flat=True)

        service_list = UmOscServiceProfileV.objects.filter(
            uniqname=osc_user, 
            service_status_code="In Service", 
            subscriber_status="Active", 
            deptid__in=dept_list,
        )

        
        record_list = []
        for record in service_list:
            parts = record.mrc_exp_chartfield.split('-')
            record.fund = parts[0]
            record.program = parts[2]
            record.chartcom_class = parts[3]

            record_list.append(record)

        print(osc_user)
        print(logged_in_user)

        return render(request, 'oscauth/numbertable.html', {'records': record_list,'unique_id':osc_user})

    else:
        return HttpResponse('<div>Invalid request method</div>')