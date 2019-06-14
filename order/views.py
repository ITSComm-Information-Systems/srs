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

from .models import Product, Action, Service, Step, Element, Item, Constant, Chartcom

def submit_order(request):
    if request.method == "POST":
        c = Cart.objects.get(username=request.user.username)
        create_preorder(c)

    else:
        print('fourOfour')

    #return ('thanks')
    return HttpResponseRedirect('/orders/cart/')

def create_preorder(cart):

    item_list = Item.objects.filter(cart=cart.id)

    for item in item_list:
        api = UmOscPreorderApiV()
        api.add_info_text_3 = cart.id
        api.add_info_text_4 = item.id
        print(item.data)

        action_id = item.data['action_id']
        cons = Constant.objects.filter(action=action_id)
        for con in cons:             #Populate the model with constants
            setattr(api, con.field, con.value)
        
        #for key, value in item.data.items():
        #    if value:           #Populate the model with user supplied values
        #        setattr(api, key, value)
        #        print(key + '>' + value +'<')

    api.save()
    print('saved')


def add_to_cart(request):
    if request.method == "POST":
        print(request.POST)
        form = FeaturesForm(request.POST)

        if form.is_valid():
            #print(form.cleaned_data['occ'])
            print('valid')

        else:
            print('bad form')
    else:
        form = PostForm()

    #c, created = Cart.objects.get_or_create(number='Not Submitted', description='Order',username=request.user.get_username())

    print(request.user.id)
    i = Item()
    #i.cart = c
    i.created_by_id = request.user.id
    i.description = request.POST['action']
    occ = request.POST['OneTimeCharges']
    print(request.POST)
    print(occ)
    i.chartcom = Chartcom.objects.get(id=occ)
    i.data = request.POST
    i.save()


    #return render(request, 'blog/post_edit.html', {'form': form})

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
                        #field = forms.ChoiceField(label=element.label, widget=forms.RadioSelect, choices=(('Y', 'Yes',), ('N', 'No',)))
                        field = forms.ChoiceField(label=element.label, choices=(('Y', 'Yes',), ('N', 'No',)))
                    elif element.type == 'Radio':
                        field = forms.ChoiceField(label=element.label, choices=eval(element.attributes))

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


class UserCart(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request):
        return HttpResponseRedirect('/orders/cart/' + request.POST['deptid'])

    def get(self, request, deptid):
        dept_list = AuthUserDept.objects.filter(user=request.user.id).exclude(dept='All').order_by('dept').distinct('dept')

        for dept in dept_list:
            deptinfo = UmOscDeptProfileV.objects.get(deptid=dept.dept)
            dept.name = deptinfo.dept_name

            if deptid == int(dept.dept):
                department = {'id': dept.dept, 'name': deptinfo.dept_name}

        if deptid == 0:
            department = {'id': dept_list[0].dept, 'name':dept_list[0].name}
            deptid = dept_list[0].dept

        item_list = Item.objects.filter(deptid=deptid)
        chartcoms = item_list.distinct('chartcom')
        action_list = Action.objects.all()

        for acct in chartcoms:
            acct.items = item_list.filter(chartcom=acct.chartcom)
            print(acct.chartcom.account_number)

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


class Services(View):

    def get(self, request):
        u = request.user
        p = u.user_permissions.all()
        for x in p:
            print(x)

        template = loader.get_template('order/service.html')
        action_list = Action.objects.all().order_by('service','display_seq_no')
        service_list = Service.objects.all().order_by('display_seq_no')

        for service in service_list:
            service.actions = action_list.filter(service=service)

        context = {
            #'title': 'Request Service',
            'service_list': service_list,
        }
        return HttpResponse(template.render(context, request))
