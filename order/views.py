from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from django.views.generic import View
from order.forms import *
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from project.pinnmodels import UmOscPreorderApiV, UmOscDeptProfileV, UmOscServiceLocV
from oscauth.models import AuthUserDept
from django.contrib.auth.mixins import PermissionRequiredMixin
from pages.models import Page
from django.http import JsonResponse

import threading

from .models import Product, Action, Service, Step, Element, Item, Constant, Chartcom, Order


def get_phone_location(request, phone_number):
    #phone_number = request.GET.get('username', None)
    loc = UmOscServiceLocV.objects.filter(service_number=phone_number).latest('billing_date')
    print(loc)
    data = {
        'code': loc.building_id,
        'name': loc.building,
        'floor': loc.floor,
        'room': loc.room,
        'jack': loc.jack
    }
    return JsonResponse(data)

class ManageChartcom(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request):
        print(request.POST)
        return HttpResponseRedirect('/orders/chartcom/' + request.POST['deptid'])

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

        template = loader.get_template('order/manage_chartfield.html')
        context = {
            'title': 'Manage Chartfields',
            'department': department,
            'dept_list': dept_list,
            'chartcoms': chartcoms,
        }
        return HttpResponse(template.render(context, request))


class Submit(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request):
        print(request)

        order_list = request.POST.getlist('order[]')

        for order in order_list:

            order_items = request.POST.getlist('orderItems[' + order +']')
            priority = request.POST['processingTime[' + order +']']
            firstitem = Item.objects.get(id=order_items[0])
            action = firstitem.data['action_id']
            service = Action.objects.get(id=action).service
 

            order = Order()  # Create new order and tie items to it.
            order.order_reference = 'TBD'
            order.created_by_id = request.user.id
            order.chartcom = firstitem.chartcom
            order.service = service
            order.status = 'Submitted'
            order.save()

            Item.objects.filter(id__in=order_items).update(order=order) #associate Items with order
            thread = threading.Thread(target=order.create_preorder)
            thread.start()

        return HttpResponseRedirect('/submitted') 


def add_to_cart(request):
    if request.method == "POST":
        i = Item()
        i.created_by_id = request.user.id
        i.description = request.POST['action']
        occ = request.POST['oneTimeCharges']
        charge = Chartcom.objects.get(id=occ)
        i.chartcom = charge
        i.deptid = charge.dept
        i.data = request.POST
        i.save()
        return HttpResponseRedirect('/orders/cart/' + charge.dept) 

def delete_from_cart(request):
    if request.method == "POST":
        item = request.POST['itemId']
        Item.objects.filter(id=item).delete()
        dept = request.POST['itemIdDept']
        return HttpResponseRedirect('/orders/cart/' + dept) 

class Workflow(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def get(self, request, action_id):

        tabs = Step.objects.filter(action = action_id).order_by('display_seq_no')
        action = Action.objects.get(id=action_id)

        for index, tab in enumerate(tabs, start=1):
            tab.step = 'step' + str(index)

            if tab.custom_form == '':
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

                    field.type = element.type                
                    f.fields.update({element.name: field})

                tab.form = f
            else:
                tab.form = globals()[tab.custom_form]

        return render(request, 'order/workflow.html', 
            {'title': action.label,
            'wfid':action_id,
            'tab_list': tabs})


class Cart(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request):
        return HttpResponseRedirect('/orders/cart/' + request.POST['deptid'])

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

        status = ['Ready to Order','Saved for Later']
        item_list = Item.objects.filter(deptid=deptid).exclude(order_id__gt=0).order_by('chartcom','-create_date')
        chartcoms = item_list.distinct('chartcom') #, 'chartcom_id')
        saved = item_list.distinct('chartcom')

        #print(item_list)

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
            'department': department,
            'dept_list': dept_list,
            'acct': chartcoms,
            'status': status,
        }
        return HttpResponse(template.render(context, request))


class Review(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request):
        print(request.POST)
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


class Services(View):
    permission_required = 'oscauth.can_order'
    
    def get(self, request):

        link_list = Page.objects.get(permalink='/links')

        template = loader.get_template('order/service.html')
        action_list = Action.objects.all().order_by('service','display_seq_no')
        service_list = Service.objects.all().order_by('display_seq_no')

        for service in service_list:
            service.actions = action_list.filter(service=service)

        context = {
            'title': 'Request Service',
            'service_list': service_list,
            'link_list': link_list,
            'page_name': 'Request Service'
        }
        return HttpResponse(template.render(context, request))


class Status(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

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

        status_help = Page.objects.get(permalink='/status')

        #items_selected = request.POST.getlist('includeInOrder')
        #order_list = item_list.distinct('chartcom')
        chartcoms = Chartcom.objects.filter(dept__in=dept_list);
        order_list = Order.objects.filter(chartcom__in=chartcoms).order_by('-create_date')

        item_list = Item.objects.filter(order__in=order_list)

        print('get items')
        for num, order in enumerate(order_list, start=1):
            if order.order_reference == 'TBD':
                order.items = item_list.filter(order=order)
            else:
                pin = UmOscPreorderApiV.objects.get(pre_order_number=order.order_reference,pre_order_issue=1)
                order.items = [{'description': pin.comment_text}]

        print('render')
        template = loader.get_template('order/status.html')
        context = {
            'title': 'Track Orders',
            'dept_list': dept_list,
            'order_list': order_list,
            'status_help': status_help,
        }
        return HttpResponse(template.render(context, request))
