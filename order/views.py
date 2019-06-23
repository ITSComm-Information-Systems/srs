from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from django.views.generic import View
from order.forms import *
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from project.pinnmodels import UmOscPreorderApiV, UmOscDeptProfileV
from oscauth.models import AuthUserDept
from django.contrib.auth.mixins import PermissionRequiredMixin
from pages.models import Page

from .models import Product, Action, Service, Step, Element, Item, Constant, Chartcom, Order


class Submit(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request):

        order_list = request.POST.getlist('order[]')

        for order in order_list:

            order_items = request.POST.getlist('orderItems[' + order +']')
            priority = request.POST['processingTime[' + order +']']
            firstitem = Item.objects.get(id=order_items[0])
            action = firstitem.data['action_id']
            service = Action.objects.get(id=action).service
 

            o = Order()
            o.order_reference = 'TBD'
            o.created_by_id = request.user.id
            o.chartcom = firstitem.chartcom
            o.service = service
            o.status = 'Submitted'
            o.save()

            Item.objects.filter(id__in=order_items).update(order=o)

        #self.create_preorder(order_items)  # move this to batch processing
        return HttpResponseRedirect('/submitted') 

        template = loader.get_template('order/order_submitted.html')
        context = {
            'order_list': order_list,
        }
        return HttpResponse(template.render(context, request))

    def create_preorder(self, order_items):

        item_list = Item.objects.filter(id__in=order_items)

        elements = Element.objects.exclude(target__isnull=True).exclude(target__exact='')
        map = {}

        for element in elements:
            map[element.name] = element.target

        for item in item_list:
            api = UmOscPreorderApiV()
            #api.add_info_text_3 = cart.id
            api.add_info_text_4 = item.id
            action_id = item.data['action_id']

            cons = Constant.objects.filter(action=action_id)
            for con in cons:             #Populate the model with constants
                setattr(api, con.field, con.value)
                print('Set:' + con.field + '=' + con.value )
                
            for key, value in item.data.items():
                if value:           #Populate the model with user supplied values
                    target = map.get(key)
                    if target != None:
                        setattr(api, target, value)
                        print('Set:' + target + '=' + value )

            api.save()
            print('API Record Saved')

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

    return HttpResponseRedirect('/orders/cart/0') 

class Workflow(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def get(self, request, action_id):
    #def get_workflow(request, action_id):

        tabs = Step.objects.filter(action = action_id).order_by('display_seq_no')
        action = Action.objects.get(id=action_id)

        for index, tab in enumerate(tabs, start=1):
            tab.step = 'step' + str(index)

            if tab.custom_form == '':
                f = forms.Form()
                f.template = 'order/dynamic_form.html'
                element_list = Element.objects.all().filter(step_id = tab.id).order_by('display_seq_no')

                for element in element_list:
                    if element.type == 'YN':
                        field = forms.ChoiceField(label=element.label, widget=forms.RadioSelect, choices=(('Y', 'Yes',), ('N', 'No',)))
                        #field = forms.ChoiceField(label=element.label, choices=Chartcom.get_user_chartcoms())
                    elif element.type == 'Radio':
                        field = forms.ChoiceField(label=element.label
                                                , choices=eval(element.attributes))


                    elif element.type == 'Chart':
                        field = forms.ChoiceField(label=element.label
                                                , widget=forms.Select(attrs={'class': "form-control"}), choices=Chartcom.get_user_chartcoms(request.user.id))
                                                                                #AuthUserDept.get_order_departments(request.user.id)


                    elif element.type == 'ST':
                        field = forms.CharField(label=element.label)
                    elif element.type == 'PH':
                        field = forms.ChoiceField(label=element.label, widget=PhoneSetType, choices=(('B', 'Basic',), ('A', 'Advanced',),('V', 'VOIP',)))
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


        item_list = Item.objects.filter(deptid=deptid,order__isnull=True)
        chartcoms = item_list.distinct('chartcom')
        action_list = Action.objects.all()

        for acct in chartcoms:
            acct.items = item_list.filter(chartcom=acct.chartcom)

            for item in acct.items:
                item.details = item.data.get('action')
                item.service = action_list.get(id=item.data.get('action_id')).service

        template = loader.get_template('order/cart.html')
        context = {
            'department': department,
            'dept_list': dept_list,
            'acct': chartcoms,
        }
        return HttpResponse(template.render(context, request))


class Review(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request):

        items_selected = request.POST.getlist('includeInOrder')
        item_list = Item.objects.filter(id__in=items_selected)
        order_list = item_list.distinct('chartcom')

        for num, order in enumerate(order_list, start=1):
            order.items = item_list.filter(chartcom=order.chartcom)
            order.num = num

        template = loader.get_template('order/review_order.html')
        context = {
            'order_list': order_list,
        }
        return HttpResponse(template.render(context, request))


class Services(View):

    def get(self, request):

        link_list = Page.objects.get(permalink='/links')

        template = loader.get_template('order/service.html')
        action_list = Action.objects.all().order_by('service','display_seq_no')
        service_list = Service.objects.all().order_by('display_seq_no')

        for service in service_list:
            service.actions = action_list.filter(service=service)

        context = {
            'service_list': service_list,
            'link_list': link_list,
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
        order_list = Order.objects.all()
        item_list = Item.objects.filter(order__in=order_list)

        for num, order in enumerate(order_list, start=1):
            order.items = item_list.filter(order=order)
            order.num = num

        template = loader.get_template('order/status.html')
        context = {
            'dept_list': dept_list,
            'order_list': order_list,
            'status_help': status_help,
        }
        return HttpResponse(template.render(context, request))
