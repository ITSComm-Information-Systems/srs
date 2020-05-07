from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from django.views.generic import View
from order.forms import *
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from project.pinnmodels import UmOscPreorderApiV, UmOscDeptProfileV, UmOscServiceProfileV, UmOscChartfieldV
from oscauth.models import AuthUserDept
from pages.models import Page
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from pages.models import Page
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from ast import literal_eval
import cx_Oracle
import json
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt

import threading

from .models import Product, Action, Service, Step, Element, Item, Constant, Chartcom, Order, LogItem, Attachment, ChargeType, UserChartcomV

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

#@permission_required('oscauth.can_order')
def send_tab_data(request):

    tab_name = request.POST.get('tab')
    print(request.POST)
    if tab_name == 'Review':
        item = Item.objects.get(id = request.POST['item_id'])


        label = Action.objects.get(id=request.POST['action_id']).cart_label

        x = label.find('[', 0)
        y = label.find(']', x)

        while x > 0:
            tag = label[x+1:y]
            element = request.POST[tag]
            label = label.replace('['+tag+']', element)
            x = label.find('[', x)
            y = label.find(']', x)


        if request.POST['cart']=='True':
            item.deptid = Chartcom.objects.get(id=item.chartcom_id).dept
            item.description = label
            item.save()
            return JsonResponse({'redirect': f'/orders/cart/{item.deptid}'}, safe=False)
        else:
            item.submit_incident()
            return JsonResponse({'redirect': '/requestsent'}, safe=False)

    step = Step.objects.get(name=tab_name)
    sequence = request.POST.get('sequence')
    visible = request.POST.get('visible')
    item_id = request.POST.get('item_id')

    #try:  TODO
    f = globals()[step.custom_form](step
        , request.POST     # Bind the form
        , request=request) # Pass entire request so user, etc is available for validation routines
    #except: 
    #    f = TabForm(step)

    if f.is_valid():
        valid = True
        summary = f.get_summary(visible)
        tab = {'title': step.label, 'fields': summary}
        data = request.POST.dict()
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
            f = globals()[step.custom_form](step, request=request)
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
        dept_list = AuthUserDept.get_order_departments(request.user.id)

        for dept in dept_list:
            deptinfo = UmOscDeptProfileV.objects.get(deptid=dept.dept)
            dept.name = deptinfo.dept_name

            if deptid == int(dept.dept):
                department = {'id': dept.dept, 'name': deptinfo.dept_name}

        if deptid == 0:
            department = {'id': dept_list[0].dept, 'name':dept_list[0].name}
            deptid = dept_list[0].dept

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
        subject = request.POST['emailSubject'] + ' question from: ' + request.user.username
        body = request.POST['emailBody'] 
        address = request.POST.get('emailAddress', 'ITCOM.csr@umich.edu')

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

        while x > 0:
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
        js = []

        for index, tab in enumerate(tabs, start=1):
            tab.step = 'step' + str(index)

            if tab.custom_form == '': #Deprecated
                f = forms.Form()
                f.template = 'order/dynamic_form.html'
                element_list = Element.objects.all().filter(step_id = tab.id).order_by('display_seq_no')

                for element in element_list:
                    if element.type == 'Radio':
                        field = forms.ChoiceField(label=element.label
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
                tab.form = globals()[tab.custom_form](tab, request=request)
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

        dept_list = Item.objects.filter(deptid__in=depts).exclude(order_id__gt=0).distinct('deptid')
        if deptid == 0 and len(dept_list) > 0:
            deptid = int(dept_list[0].deptid)

        for dept in dept_list:
            deptinfo = UmOscDeptProfileV.objects.get(deptid=dept.deptid)
            dept.active = deptinfo.dept_eff_status
            dept.name = deptinfo.dept_name

            if deptid == int(dept.deptid):
                first = {'id': dept.deptid, 'name': deptinfo.dept_name}


        status = ['Ready to Order','Saved for Later']
        item_list = Item.objects.filter(deptid=deptid).exclude(order_id__gt=0).order_by('chartcom','-create_date')
        chartcoms = item_list.distinct('chartcom') #, 'chartcom_id')
        saved = item_list.distinct('chartcom')

        #item_list = Item.objects.filter(deptid=deptid,order__isnull=True).order_by('chartcom','-create_date')

        for acct in chartcoms:
            acct.items = item_list.filter(chartcom=acct.chartcom,order__isnull=True) #.order_by('create_date')
            acct.table = 'tableReady' + str(acct.chartcom_id)

        status[0] = chartcoms
        status[0].label = 'Ready to Order'
        status[0].id = 'tableReady'        

        item_list = Item.objects.filter(deptid=deptid,order=0).order_by('chartcom','-create_date')
        #saved_later = item_list.distinct('chartcom')

        for acct in saved:
            acct.items = item_list.filter(chartcom=acct.chartcom) #.order_by('create_date')
            acct.table = 'tableSaved' + str(acct.chartcom_id)

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
        order_list = item_list.distinct('chartcom')

        for num, order in enumerate(order_list, start=1):
            order.items = item_list.filter(chartcom=order.chartcom)
            order.num = num

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

        for service in service_list:
            service.actions = action_list.filter(service=service)

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
     
        order_list = Order.objects.filter(chartcom__dept__in=auth_dept_list).order_by('-create_date', 'id').select_related()
        item_list = Item.objects.filter(order__in=order_list).order_by('-order__create_date', 'order_id')

        order_id_list = list(str(order.id) for order in order_list)
        pins = UmOscPreorderApiV.objects.filter(add_info_text_3__in=order_id_list,pre_order_issue=1)

        depts = set()
        i = 0
        x = len(item_list)
        
        for order in order_list:
            depts.add(order.chartcom.dept)
            order.deptid = order.chartcom.dept
            pin = next((x for x in pins if x.add_info_text_3 == str(order.id)), None)
            order.srs_status = "Submitted"
            if pin:
                if(pin.work_status_name == "Received"):
                    order.srs_status = "Submitted"
                if pin.status_code == 2:
                    if(pin.work_status_name == "Cancelled"):
                        order.srs_status = "Cancelled"
                    else:
                        order.srs_status = "Completed"

            order.items = []

            while item_list[i].order_id == order.id and i < x-1:
                order.items.append(item_list[i])
                i = i + 1

        dept_list = UmOscDeptProfileV.objects.filter(deptid__in=depts).order_by('deptid')

        if deptid == 0:
            department = {'id': dept_list[0].deptid, 'name':dept_list[0].dept_name}
            deptid = dept_list[0].deptid 
                    
        template = loader.get_template('order/status.html')
        context = {
            'title': 'Track Orders',
            'dept_list': dept_list,
            'order_list': order_list,
            'status_help': Page.objects.get(permalink='/status'),
        }
        return HttpResponse(template.render(context, request))
