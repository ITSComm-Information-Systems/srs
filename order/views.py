from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import Http404
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from order.forms import *
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from project.pinnmodels import UmOscPreorderApiV, UmOscDeptProfileV, UmOscServiceProfileV, UmOscChartfieldV
from project.models import Email
from oscauth.models import AuthUserDept
from pages.models import Page
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from pages.models import Page
from django.http import JsonResponse
from project.integrations import create_ticket_server_delete
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from ast import literal_eval
import re
import json
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt

from oscauth.utils import get_mc_user

import threading

from .models import Product, Action, Service, Step, Element, Item, Constant, Chartcom, Order, LogItem, Attachment, ChargeType, UserChartcomV

#import for filter
import datetime
from django.db.models import Case, When, Value, F


@permission_required('oscauth.can_order')
def get_phone_location(request, phone_number):
    locations = list(UmOscServiceProfileV.objects.filter(service_number=phone_number).exclude(location_id=0).values())
    if not locations:
        phone_number = phone_number.replace("-",'')
        locations = list(UmOscServiceProfileV.objects.filter(service_number=phone_number).exclude(location_id=0).values())

    if locations:
        phone_dept = locations[0]['deptid']
        authorized_departments = AuthUserDept.get_order_departments(request.user)

        authorized = False

        for dept in authorized_departments:
            if dept.dept == phone_dept:
                authorized = True

        locations[0]['authorized'] = authorized

    return JsonResponse(locations, safe=False)



@permission_required('oscauth.can_order')
def get_phone_information(request, uniqname):
    authorized_departments = AuthUserDept.get_order_departments(request.user)

    service_list = list(UmOscServiceProfileV.objects.filter(
            uniqname=uniqname, 
            service_status_code="In Service", 
            subscriber_status="Active", 
            deptid__in=authorized_departments,
        ).values())

    record_list = []
    for record in service_list:
        parts = record["mrc_exp_chartfield"].split('-')
        record["fund"] = parts[0]
        record["program"] = parts[2]
        record["chartcom_class"] = parts[3]

        record_list.append(record)
    
    return JsonResponse(record_list, safe=False)


def querydict_to_dict(query_dict):  # Kudos to QFXC on StackOverflow
    data = {}
    for key in query_dict.keys():
        v = query_dict.getlist(key)
        if len(v) == 1:
            v = v[0]
        data[key] = v
    return data
 

def  send_ticket(owner, user):

    client_id = settings.UM_API['CLIENT_ID']
    auth_token = settings.UM_API['AUTH_TOKEN']
    base_url = settings.UM_API['BASE_URL']

    headers = { 
        'Authorization': f'Basic {auth_token}',
        'accept': 'application/json'
        }

    url = f'{base_url}/um/it/oauth2/token?grant_type=client_credentials&scope=tdxticket'
    response = requests.post(url, headers=headers)
    response_token = json.loads(response.text)
    access_token = response_token.get('access_token')

    headers = {
        'X-IBM-Client-Id': client_id,
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json' 
        }

    payload = {
        "FormID": 441,
        "TypeID": 5,
        "SourceID": 4,
        "StatusID": 77,
        "ServiceID": 213,  # No workflow
        "PriorityID": 20,
        "ResponsibleGroupID": 18,
        "Title": "MiServer Migration Assistance",
        "RequestorEmail": user.email,
        "Attributes": [
            {"ID": "1951",
            "Value": "200"},
            {"ID": "1953",
            "Value": owner}
            ]
        }

    data_string = json.dumps(payload)
    response = requests.post( base_url + '/um/it/31/tickets', data=data_string, headers=headers )


#@permission_required('oscauth.can_order')
def send_tab_data(request):

    tab_name = request.POST.get('tab')
    action = Action.objects.get(id=request.POST.get('action_id'))

    if tab_name == 'Review':
        item = Item.objects.get(id = request.POST['item_id'])


        label = Action.objects.get(id=request.POST['action_id']).cart_label

        x = label.find('[', 0)
        y = label.find(']', x)

        while x >= 0:
            tag = label[x+1:y]
            element = request.POST.get(tag, '')
            label = label.replace('['+tag+']', element)
            x = label.find('[', x)
            y = label.find(']', x)


        if request.POST['cart']=='True':
            item.deptid = Chartcom.objects.get(id=item.chartcom_id).dept
            item.description = label
            item.save()
            return JsonResponse({'redirect': f'/orders/cart/{item.deptid}'}, safe=False)
        else:
            data_changed_not_shortcode = False
            action_name = request.POST.get('action')
            if action_name == 'Modify MiServer':
                data = item.data
                review_summary = data['reviewSummary']
                pattern = r'^\*'
                for entry in review_summary:
                    title = entry['title']
                    row = entry['fields']
                    if (title == 'Server Specification'):
                        for data in row:
                            label = data['label']
                            if label == 'Disk Space':
                                disk_list = data['list']
                                for disk in disk_list:
                                    if disk[-1] == '*':
                                        data_changed_not_shortcode = True
                    for data in row:
                        label = data['label']
                        if re.match(pattern, label):
                            if label != '*Enter a Billing Shortcode for costs to be billed to':
                                data_changed_not_shortcode = True
                item.description = label
                item.save()
                if data_changed_not_shortcode: item.route()
                else: 
                    item.route(skip_submit_incident=True)
            else:
                item.description = label
                item.save()
                item.route()

            
            

            
            return JsonResponse({'redirect': '/requestsent'}, safe=False)

    step = Step.objects.get(name=tab_name)
    sequence = request.POST.get('sequence')
    visible = request.POST.get('visible')
    item_id = request.POST.get('item_id')

    #try:  TODO
    f = globals()[step.custom_form](step, action
        , request.POST     # Bind the form
        , request=request) # Pass entire request so user, etc is available for validation routines
    #except: 
    #    f = TabForm(step)

    if f.is_valid():

        if request.POST.get('misevexissev') == 'yesexis':
            send_ticket(request.POST.get('owner'), request.user)
            return JsonResponse({'redirect': '/requestsent'}, safe=False)

        valid = True
        summary = f.get_summary(visible)
        tab = {'title': step.label, 'fields': summary}
        data = querydict_to_dict(request.POST)
        data['csrfmiddlewaretoken'] = ''
        action = Action.objects.get(id=request.POST.get('action_id'))

        if int(item_id) == 0:
            i = Item()
            i.created_by_id = request.user.id
            i.description = ' '
            data['reviewSummary'] = [tab]
            data['tab_list'] = action.get_tab_list()
            i.deptid = '1'
            i.chartcom_id = 14388  #TODO need default chartcom
        else:
            i = Item.objects.get(id=item_id)
            review_summary = i.data['reviewSummary']
            data['tab_list'] = i.data['tab_list']
            tabnum = int(sequence) - 1
            if len(review_summary) < int(sequence):
                review_summary.append(tab)
            else:
                review_summary[tabnum] = tab
            data['reviewSummary'] = review_summary

        i.chartcom_id = request.POST.get('oneTimeCharges', 14388)
        i.data = data
        i.description = action.cart_label
        i.save()
        item_id = i.id

        #step = Step.objects.get(name='detailsNFS')
        
        if request.POST.get('volaction'):
            tab_name = 'Review'
            step = Step.objects.get(name='Review')
        else:
            for index, tab in enumerate(i.data['tab_list'], start=0):
                if tab['name'] == request.POST.get('tab'):
                    next_tab = i.data['tab_list'][index+1]
                    tab_name = next_tab['name']
                    step = Step.objects.get(name=next_tab['name'])
                    break

        try:
            f = globals()[step.custom_form](step, action, request=request)
        except:
            print('bind form tab error')
            f = TabForm(step)
        
        if step.name == 'Review':
            f.data = i.data['reviewSummary']

    else:
        valid = False

    tab_content = loader.render_to_string(f.template, {'tab': {'form': f}})

    return JsonResponse({'valid': valid
                        ,'item_id': item_id
                        ,'tab_name': tab_name
                        ,'tab_content': tab_content}, safe=False)


@permission_required('oscauth.can_order')
def get_order_detail(request, order_id):

    order = Order.objects.get(id=order_id)
    item_list = Item.objects.filter(order=order)


    template = loader.get_template('order/order_detail.html')
    context = {
        'title': 'Order Summary',
        'order': order,
        'item_list': item_list
    }
    return HttpResponse(template.render(context, request))



class ManageChartcom(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request):
        action = request.POST.get('action')
        id = request.POST.get('chartcomId')
        deptid = request.POST.get('deptid')
        
        if action == 'add':
            cc = UmOscChartfieldV.objects.get(chartfield=request.POST.get('chartfieldSelection'))
            chartcom = Chartcom()
            chartcom.fund = cc.fund
            chartcom.dept = cc.deptid
            chartcom.program = cc.program
            chartcom.class_code = cc.class_code
            chartcom.project_grant = cc.project_grant
            chartcom.short_code = cc.short_code
            chartcom.name = request.POST.get('description')
            chartcom.save()

        if action == 'edit':
            chartcom = Chartcom.objects.get(id=id)
            #descr = request.POST.get('newDescription')
            chartcom.name = request.POST.get('newDescription')
            chartcom.save()

        if action == 'delete':
            x = Chartcom.objects.get(id=id).delete()

        return HttpResponseRedirect('/orders/chartcom/' + deptid)

    def get(self, request, deptid):
        dept_list = AuthUserDept.get_order_departments(request.user.id).order_by('dept')

        for dept in dept_list:
            deptinfo = UmOscDeptProfileV.objects.get(deptid=dept.dept)
            dept.name = deptinfo.dept_name

            if deptid == int(dept.dept):
                department = {'id': dept.dept, 'name': deptinfo.dept_name}

        if deptid == 0:
            try:
                department = {'id': dept_list[0].dept, 'name':dept_list[0].name}
                deptid = dept_list[0].dept
            except:
                department = ''
                deptid = 0

        chartcoms = Chartcom.objects.filter(dept=deptid)
        add_chartcoms = UmOscChartfieldV.objects.filter(deptid=deptid)

        short_code_list = {}
        for ctc in add_chartcoms:
            short_code_list[str(ctc.chartfield)] = ctc.short_code

        template = loader.get_template('order/manage_chartfield.html')
        context = {
            'title': 'Manage Chartfields',
            'department': department,
            'dept_list': dept_list,
            'chartcoms': chartcoms,
            'add_chartcoms': add_chartcoms,
            'short_code_list':json.dumps(short_code_list),
        }
        return HttpResponse(template.render(context, request))


class Submit(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request):

        order_list = request.POST.getlist('order[]')

        for order in order_list:

            order_items = request.POST.getlist('orderItems[' + order +']')
            priority = request.POST['processingTime[' + order +']']
            due_date = None

            if priority == 'expediteOrder':
                due_date = request.POST['expediteDayInput[' + order +']']

            if priority == 'specificDay':
                due_date = request.POST['specificDayInput[' + order +']']

            firstitem = Item.objects.get(id=order_items[0])
            action = firstitem.data['action_id']
            service = Action.objects.get(id=action).service
 

            order = Order()  # Create new order and tie items to it.
            order.order_reference = 'TBD'
            order.created_by_id = request.user.id
            order.chartcom = firstitem.chartcom
            order.service = service
            #order.status = 'Submitted'
            if priority == 'expediteOrder':
                order.priority = 'High'
            order.due_date = due_date
            order.save()

            Item.objects.filter(id__in=order_items).update(order=order) #associate Items with order
            thread = threading.Thread(target=order.create_preorder)
            thread.start()

        return HttpResponseRedirect('/submitted') 

@csrf_exempt
def send_email(request):   #Pinnacle will route non prod emails to a test address
    if request.method == "POST":
        subject = request.POST.get('emailSubject') + ' question from: ' + request.user.username
        body = request.POST['emailBody'] 
        address = (request.POST.get('emailAddress', 'ITCOM.csr@umich.edu'))
        print(request.POST)


        with connections['pinnacle'].cursor() as cursor:
            cursor.callproc('um_osc_util_k.um_send_email_p', [address, body, subject])
        if body == "Cancel Order":
            return HttpResponseRedirect('/cancelorder') 
        return HttpResponseRedirect('/emailsent') 


@permission_required('oscauth.can_order')
def add_to_cart(request):
    if request.method == "POST":

        i = Item()
        i.created_by_id = request.user.id

        label = Action.objects.get(id=request.POST['action_id']).cart_label

        x = label.find('[', 0)
        y = label.find(']', x)

        while x >= 0:
            tag = label[x+1:y]
            element = request.POST[tag]
            label = label.replace('['+tag+']', element)
            x = label.find('[', x)
            y = label.find(']', x)

        summary = request.POST['reviewSummary']

        title = ''
        data = []

        for line in summary.split('^'):

            if line[0:1] == '~':
                if title:
                    tab = {'title': title, 'fields': tabdata}
                    data.append(tab)
                    
                tabdata = []
                title = line[1:99]
            else:
                fields = line.split('\t')

                if len(fields) > 1:
                    tabdata.append({'label': fields[0], 'value': fields[1]})
                else:
                    if line != '':
                        tabdata.append({'label': line, 'value': ' '})
        
        tab = {'title': title, 'fields': tabdata}
        data.append(tab)

        postdata = request.POST.dict()
        
        postdata['reviewSummary'] = data
        postdata['csrfmiddlewaretoken'] = ''

        i.description = label
        occ = request.POST['oneTimeCharges']
        charge = Chartcom.objects.get(id=occ)
        i.chartcom = charge
        #i.chartcom_id = request.POST['oneTimeCharges']
        i.deptid = charge.dept
        i.data = postdata
        i.save()


        for file in request.FILES.getlist('file'):
            fs = FileSystemStorage()
            filename = fs.save('attachments/' + file.name, file)  

            attach = Attachment()
            attach.item = i
            attach.file = filename
            attach.save()

        return HttpResponseRedirect('/orders/cart/' + charge.dept) 

@permission_required('oscauth.can_order')
def delete_from_cart(request):
    if request.method == "POST":
        item = request.POST['itemId']
        Item.objects.filter(id=item).delete()
        dept = request.POST['itemIdDept']
        return HttpResponseRedirect('/orders/cart/' + dept) 


@permission_required('oscauth.admin')
def get_order_list(request):
    
    filter = {}
    if request.GET.get('filter') == 'TBD':
        filter['order_reference'] = 'TBD'

    template = loader.get_template('order/integration_list.html')
    context = {
        'title': 'Admin Order List',
        'order_list': Order.objects.all().prefetch_related('created_by','service').filter(**filter).order_by('-id'),
    }
    return HttpResponse(template.render(context, request))


class SMS(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request):
        item = Item.objects.get(id=request.POST.get('item'))
        item.external_reference_id = 0
        item.save()

        return HttpResponseRedirect('/orders/integration/sms') 


    def get(self, request):
        item_list = Item.objects.filter(description='Add SMS Text').order_by('-create_date')

        return render(request, 'order/integration_sms_list.html',  {'item_list': item_list,})


class Integration(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)

        if request.POST['action'] == 'delete':
            order.delete()
            return HttpResponseRedirect('/orders/status/0') 
        else:            
            order.create_preorder()
            return HttpResponseRedirect('/orders/integration/' + str(order_id)) 


    def get(self, request, order_id):
        order = Order.objects.get(id=order_id)
        item_list = Item.objects.filter(order=order)

        order_list = LogItem.objects.filter(local_key = str(order.id))

        preorder = UmOscPreorderApiV.objects.filter(add_info_text_3=order_id)

        for ord in order_list:
            if ord.transaction == 'JSON':
                parsed = json.loads(ord.description)
                ord.sent = json.dumps(parsed, indent=4)


        for item in item_list:
            item.note = item.format_note()
            error = LogItem.objects.filter(local_key = str(item.id))
            if error:
                item.error = error
            else:
                item.error = 'no errors'

        return render(request, 'order/integration.html', 
            {'order': order,
            'preorder': preorder,
            'order_list': order_list,
            'item_list': item_list,})


class Workflow(UserPassesTestMixin, View):

    def test_func(self):
        action_id = self.request.resolver_match.kwargs['action_id']
        action = Action.objects.get(id=action_id)

        if action.service.group_id == 2:  # MiStorage requires no permissions
            if self.request.user.is_authenticated:
                return True
            else:
                return False
        else:
            if self.request.user.has_perm('oscauth.can_order'):
                return True
            else:
                return False

    def get(self, request, action_id):

        tabs = Step.objects.filter(action = action_id).order_by('display_seq_no')
        action = Action.objects.get(id=action_id)
        request.session[action.service.group.name] = action.service.name

        js = []

        for index, tab in enumerate(tabs, start=1):
            tab.step = 'step' + str(index)

            if tab.custom_form == '': #Deprecated
                f = forms.Form()
                f.template = 'order/dynamic_form.html'
                element_list = Element.objects.all().filter(step_id = tab.id).order_by('display_seq_no')

                for element in element_list:
                    if element.type == 'Radio':
                        field = forms.ChoiceField(label=element.label, help_text = element.help_text
                                                , choices=eval(element.attributes))
                    elif element.type == 'Chart':
                        field = forms.ChoiceField(label=element.label
                                                , widget=forms.Select(attrs={'class': "form-control"}), choices=Chartcom.get_user_chartcoms(request.user.id))
                                            #AuthUserDept.get_order_departments(request.user.id)
                        field.dept_list = Chartcom.get_user_chartcom_depts(request.user.id) #['12','34','56']
                    elif element.type == 'NU':
                        field = forms.ChoiceField(label=element.label
                                                , widget=forms.NumberInput(attrs={'min': "1"}))
                    elif element.type == 'ST':
                        field = forms.CharField(label=element.label)
                    else:
                        field = forms.IntegerField(label=element.label)

                    field.display_seq_no = element.display_seq_no
                    field.display_condition = element.display_condition
                    field.type = element.type
                    f.fields.update({element.name: field})

                tab.form = f
            elif tab.custom_form == 'BillingForm':
                f = forms.Form()
                f.template = 'order/billing.html'
                f.charge_types = ChargeType.objects.filter(action__id=action_id).order_by('display_seq_no')
                f.dept_list = Chartcom.get_user_chartcom_depts(request.user.id) #['12','34','56']
                #f.chartcom_list = Chartcom.get_user_chartcoms(request.user.id)
                f.chartcom_list = UserChartcomV.objects.filter(user=request.user).order_by('name')
                tab.form = f

            elif tab.custom_form == 'StaticForm':
                tab.bodytext = Page.objects.get(permalink='/' + tab.name).bodytext
                tab.form = forms.Form()
                tab.form.template = 'order/static.html'
            else:
                if not action.use_ajax or index==1:
                    tab.form = globals()[tab.custom_form](tab, action, request=request)
                else:
                    f = forms.Form()
                    f.template = 'order/base_form.html'  # use base 4/16/2021
                    tab.form = f

                if tab.name == 'ChangeSFUser':
                    js.append('change_user')
                if tab.name == 'PhoneLocation':
                    js.append('phone_location')
                elif tab.name == 'LocationNew':
                    js.append('location')
                elif tab.name == 'SelectFeatures':
                    js.append('features')
                elif tab.name == 'AuthCodes':
                    js.append('auth_codes')
                elif tab.name == 'AuthCodeCancel':
                    js.append('auth_code_cancel')
                elif tab.name == 'CMC':
                    js.append('cmc_codes')
                elif tab.name == 'Equipment':
                    js.append('equipment')
                elif tab.name == 'QuantityModel':
                    js.append('product')
                elif tab.name == 'Contact':
                    js.append('voicemail')

        # Configurable conduit information
        conduit_check = Page.objects.get(permalink='/checkcond')
        conduit_order = Page.objects.get(permalink='/ordercond')

        return render(request, 'order/workflow.html', 
            {'title': action.label,
            'action':action,
            'tab_list': tabs,
            'js_files': js,
            'conduit_check': conduit_check,
            'conduit_order': conduit_order})


class Cart(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request):
        return HttpResponseRedirect('/orders/cart/' + request.POST['deptid'])

    def get(self, request, deptid):
        
        depts = []
        user_dept_list = AuthUserDept.get_order_departments(request.user.id)
        for dept in user_dept_list:
            depts.append(dept.dept)

        first= {}

        dept_list = Item.objects.filter(deptid__in=depts).exclude(order_id__gt=0).values('deptid').distinct()
        if deptid == 0 and len(dept_list) > 0:
            deptid = int(dept_list[0].get('deptid'))

        for dept in dept_list:
            deptinfo = UmOscDeptProfileV.objects.get(deptid=dept.get('deptid'))
            dept['active'] = deptinfo.dept_eff_status
            dept['name'] = deptinfo.dept_name

            if deptid == int(dept.get('deptid')):
                first = {'id': dept.get('deptid'), 'name': deptinfo.dept_name}


        status = ['Ready to Order','Saved for Later']
        item_list = Item.objects.filter(deptid=deptid).exclude(order_id__gt=0).order_by('chartcom','-create_date')
        chartcoms = item_list.distinct().values('chartcom','chartcom_id','chartcom__name').order_by('chartcom') #, 'chartcom_id')
        saved = item_list.distinct().values('chartcom','chartcom_id','chartcom__name').order_by('chartcom') #, 'chartcom_id')

        #item_list = Item.objects.filter(deptid=deptid,order__isnull=True).order_by('chartcom','-create_date')

        for acct in chartcoms:
            acct['items'] = item_list.filter(chartcom=acct.get('chartcom'),order__isnull=True) #.order_by('create_date')
            acct['table'] = 'tableReady' + str(acct.get('chartcom_id'))

        status[0] = chartcoms
        status[0].label = 'Ready to Order'
        status[0].id = 'tableReady'        

        item_list = Item.objects.filter(deptid=deptid,order=0).order_by('chartcom','-create_date')
        #saved_later = item_list.distinct('chartcom')

        for acct in saved:
            acct['items'] = item_list.filter(chartcom=acct.get('chartcom')) #.order_by('create_date')
            acct['table'] = 'tableSaved' + str(acct.get('chartcom_id'))

        status[1] = saved
        status[1].label = 'Saved for Later'
        status[1].id = 'tableSaved'

        template = loader.get_template('order/cart.html')
        context = {
            'title': 'Cart',
            'department': first,
            'dept_list': dept_list,
            'acct': chartcoms,
            'status': status,
        }
        return HttpResponse(template.render(context, request))


class Review(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request):
        dept = request.POST.get('deptSubmit')
        items_selected = request.POST.getlist('includeInOrder')
        item_list = Item.objects.filter(id__in=items_selected)
        order_list = item_list.values('chartcom').distinct()

        for num, order in enumerate(order_list, start=1):
            order['items'] = item_list.filter(chartcom=order.get('chartcom'))
            order['num'] = num

        template = loader.get_template('order/review_order.html')
        context = {
            'title': 'Review Order',
            'order_list': order_list,
            'dept': dept
        }
        return HttpResponse(template.render(context, request))


class Services(UserPassesTestMixin, View):

    def test_func(self):
        group_id = self.request.resolver_match.kwargs['group_id']

        if group_id == 2:  # MiStorage requires no permissions
            if self.request.user.is_authenticated:
                return True
            else:
                return False
        else:
            if self.request.user.has_perm('oscauth.can_order'):
                return True
            else:
                return False
    
    def get(self, request, group_id):

        link_list = Page.objects.get(permalink=f'/links/{group_id}')
        notices = Page.objects.get(permalink=f'/notices/{group_id}')

        template = loader.get_template('order/service.html')
        action_list = Action.objects.filter(active=True).order_by('service','display_seq_no')
        service_list = Service.objects.filter(group_id=group_id,active=True).order_by('display_seq_no')

        if group_id == 1:
            selected_service = request.session.get('Telephony','phoneData')
        else:
            selected_service = request.session.get('backupStorage','miBackup')

        for service in service_list:
            if service.name == 'cloud':
                service.actions = [{'label': 'Order Google Cloud Platform', 'target': '/services/gcp/add/'},
                                   {'label': 'View/Change GCP Project', 'target': '/services/gcp'},
                                   {'label': 'Order Microsoft Azure', 'target': '/services/azure/add/'},
                                   {'label': 'View/Change Microsoft Azure', 'target': '/services/azure'},
                                   {'label': 'Order AWS', 'target': '/services/aws/add/'},
                                   {'label': 'View/Change AWS', 'target': '/services/aws/'} ]
            elif service.name == 'midesktop':
                service.actions = [{'label': 'Order MiDesktop','target': '/services/midesktop/add/'},
                                   {'label': 'View/Change MiDesktop','target': '/services/midesktop/'},
                                   {'label': 'Create Image','target': '/services/midesktop-image/add'},
                                   {'label': 'View/Change Image','target': '/services/midesktop-image/'},
                                   {'label': 'Create Network','target': '/services/midesktop-network/add'},
                                   {'label': 'View/Change Network','target': '/services/midesktop-network/'}]
            elif service.name == 'container':
                service.actions = [{'label': 'Request Container Project', 'target': '/services/container/add/',
                                    'description': 'The ITS Container Service hosts containerized applications. A Container Project is a development environment for creating or hosting a containerized app.'}]
            else:
                service.actions = action_list.filter(service=service)
                for action in service.actions:
                    if action.id == 76:   # ToDo add target to action.
                        action.target = '/orders/sp/AddSMS'
                    else:
                        action.target = f'/orders/wf/{action.id}'

            if service.name == selected_service:
                service.active = 'active show'

        context = {
            'title': 'Request Service',
            'service_list': service_list,
            'link_list': link_list,
            'notices': notices,
            'page_name': 'Request Service'
        }
        return HttpResponse(template.render(context, request))


class Status(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'
    
    def get(self, request, deptid):
        auth_depts = AuthUserDept.get_order_departments(request.user.id)
        auth_dept_list = list(dept.dept for dept in auth_depts)
     
        year_old = datetime.date.today() - datetime.timedelta(366)

        order_list = Order.objects.filter(chartcom__dept__in=auth_dept_list,create_date__gte=year_old).order_by('-create_date', 'id').select_related()
        item_list = Item.objects.filter(order__in=order_list).order_by('-order__create_date', 'order_id')

        order_id_list = list(str(order.id) for order in order_list)
        pins = UmOscPreorderApiV.objects.filter(add_info_text_3__in=order_id_list,pre_order_issue=1)

        depts = set()
        people_list = set()
        status_list = set()
        dates_list = set()
        i = 0
        x = len(item_list)

        for order in order_list:
            order.deptid = order.chartcom.dept

            #datetime filter
            result=datetime.date.today()-order.create_date.date()
            if result<datetime.timedelta(31):
                order.timeDiff = (1,"30 days")
            elif result<datetime.timedelta(91):
                order.timeDiff = (2,"31-90 days")
            elif result<datetime.timedelta(181):
                order.timeDiff = (3,"91-180 days")
            elif result<datetime.timedelta(366):
                order.timeDiff = (4,"181-365 days")
            else:
                order.timeDiff = (5,"More than 365 days")
   
            #add status that should display in SRS
            pin = next((x for x in pins if x.add_info_text_3 == str(order.id)), None)
            order.srs_status = "Submitted"
            if pin:
                if pin.work_status_name == "Received":
                    order.srs_status= "Submitted"
                elif pin.work_status_name != '' and pin.work_status_name != None:
                    order.srs_status = pin.work_status_name
                    
                if str(pin.status_code) == '2':
                    if(pin.work_status_name == "Cancelled" or pin.work_status_name == "Withdrawn"):
                        order.srs_status = "Cancelled"
                    else:
                        order.srs_status = "Completed"

            order.items = []
            while item_list[i].order_id == order.id and i < x-1:
                order.items.append(item_list[i])
                i = i + 1
            
            people_list.add((order.created_by.username, order.deptid))
            status_list.add((order.srs_status, order.deptid))
            depts.add(order.chartcom.dept)
            dates_list.add((order.timeDiff, order.deptid))

        dept_list = UmOscDeptProfileV.objects.filter(deptid__in=depts).order_by('deptid')
        people_list=sorted(people_list)
        dates_list=sorted(dates_list, key=lambda x:x[0][0])
         
        template = loader.get_template('order/status.html')
        context = {
            'title': 'Track Orders',
            'dept_list': dept_list,
            'order_list': order_list,
            'dates_list': dates_list,
            'people_list': people_list,
            'status_list':status_list,
            'status_help': Page.objects.get(permalink='/status'),
        }
        return HttpResponse(template.render(context, request))



class DatabaseView(UserPassesTestMixin, View):

    def test_func(self):
        username = self.request.user.username
        instance_id = self.kwargs['instance_id']
        owner = Database.objects.get(id=instance_id).owner.name

        mc = MCommunity()
        mc.get_group(owner)

        if username in mc.members:
            return True
        else:
            return False
    
    def get(self, request, instance_id):
        db = Database.objects.get(id=instance_id)
        form = DatabaseForm(request.user, instance=db)

        template = loader.get_template('order/database_edit.html')
        context = {
            'title': 'Review Shared Database',
            'form': form
        }
        return HttpResponse(template.render(context, request))


    def post(self, request, instance_id):
        db = Database.objects.get(id=instance_id)
        form = DatabaseForm(request.user, request.POST, instance=db)

        if form.is_valid() and form.has_changed():
            form.save()
            return HttpResponseRedirect('/requestsent') 

        template = loader.get_template('order/database_edit.html')
        context = {
            'title': 'Review Shared Database',
            'form': form,
        }
        return HttpResponse(template.render(context, request))

def _extract_server_name(params):
    name = params.get("serverName[]", "").strip().lower()
    if name:
        return name

    name = params.get("name", "").strip().lower()
    if name:
        return name

    for key, value in params.items():
        if key.endswith('-name'):
            return value.strip().lower()

    return ""

def server_name_check(request):
    """
    HTMX endpoint to validate a proposed server name.
    Returns an HTML fragment for inline feedback.
    """
    name = _extract_server_name(request.GET)

    if not name:
        return HttpResponse("")

    # length check (DNS-safe)
    if len(name) > 63:
        return HttpResponse(
            '<div class="invalid-feedback d-block">'
            'Name must be 63 characters or fewer.'
            '</div>'
        )

    # format check
    if not CLONE_NAME_RE.match(name):
        return HttpResponse(
            '<div class="invalid-feedback d-block">'
            'Name can contain letters, numbers, and single hyphens, '
            'must start with a letter, and cannot end with a hyphen.'
            '</div>'
        )

    # availability check (case-insensitive)
    if Server.objects.filter(name__iexact=name).exists():
        return HttpResponse(
            '<div class="invalid-feedback d-block">'
            'That name is already in use.'
            '</div>'
        )

    # success
    return HttpResponse(
        '<div class="valid-feedback d-block">'
        'Name is available.'
        '</div>'
    )
class ServerView(UserPassesTestMixin, View):

    def dispatch(self, request, *args, **kwargs):
        self.server = get_object_or_404(Server, pk=kwargs["instance_id"])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        username = self.request.user.username

        mc = MCommunity()
        mc.get_group(self.server.owner.name)

        return username in mc.members
    
    def get(self, request, instance_id, action):

        server = get_object_or_404(Server, pk=instance_id)
        formset = None

        if action == 'delete':
            template = loader.get_template('order/server_delete.html')
            title = 'Delete Server'
        elif action == 'clone':
            template = loader.get_template('order/server_clone.html')
            formset = CloneServerNameFormSet(prefix='clone')
            title = 'Clone Server'
        else:
            raise Http404

        context = {
            'title': title,
            'server': server,
            'formset': formset,
        }
        return HttpResponse(template.render(context, request))


    def post(self, request, instance_id, action):
        instance = get_object_or_404(Server, pk=instance_id)
        if action == 'delete':
            create_ticket_server_delete(instance, request.user, f'End Service for {instance.name}')

            current_time = datetime.datetime.now()
            formatted_date = current_time.strftime('%Y%m%d')
            suffix = "-Ended-" + formatted_date
            instance.name = instance.name + suffix

            instance.in_service = False
            instance.save()

            return HttpResponseRedirect('/requestsent')

        if action == 'clone':
            formset = CloneServerNameFormSet(request.POST, prefix='clone')
            if formset.is_valid():
                for clone in formset.cleaned_data:
                    new_server = instance.clone(clone['name'])

                return HttpResponseRedirect('/requestsent')

            template = loader.get_template('order/server_clone.html')
            context = {
                'title': 'Clone Server',
                'server': instance,
                'formset': formset,
            }
            return HttpResponse(template.render(context, request))

        raise Http404
    

class AddSMS(PermissionRequiredMixin, View):
    title = 'Add SMS for Zoom Phone'
    permission_required = 'oscauth.can_order'
    form = AddSMSForm
    template = 'order/add_sms.html'

    def get(self, request):

        return render(request, self.template, 
                    {
                        'title': self.title,
                        'form': self.form(),
                    })

    
    def post(self, request):

        if request.POST.get('submit'):  # Already validated uniqname and retrieved associated phone numbers.
            user_id = request.POST.get('user_id')
            service_numbers = request.POST.getlist('service_number')

            from project.pinnmodels import UmOscServiceProfileV as ServiceNumbers
            for number in ServiceNumbers.objects.filter(service_number__in=service_numbers, service_status_code='In Service', uniqname=user_id):
                print(number, number.mrc_exp_chartfield)

                with connections['pinnacle'].cursor() as cursor:
                    cursor.callproc('pinn_custom.um_osc_util_k.um_add_generic_mrc_p', 
                                    [number.subscriber_id, number.service_id, 'FT-ZOOM-SMS', 1, number.mrc_exp_chartfield])

            Item.objects.create(description='Add SMS Text', chartcom_id=14388, created_by_id=request.user.id, internal_reference_id=76
                                , data={'user_id': user_id, 'service_numbers': service_numbers})

            email = Email.objects.get(code='SMS_REQUEST')
            email.to = user_id + '@umich.edu'
            email.cc = request.user.email
            email.context = {"uniqname": user_id }
            email.send()

            return HttpResponseRedirect('/requestsent')

        form = self.form(request.POST, request=request)
        form.is_valid()

        return render(request, self.template, 
                    {
                        'title': self.title,
                        'form': form,
                    })
