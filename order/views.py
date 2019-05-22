from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from order.forms import *
from project.pinnmodels import UmOscPreorderApiV

from .models import Cart, Product, Action, Service, Step, Element, Item, Constant

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

    c, created = Cart.objects.get_or_create(number='Not Submitted', description='Order',username=request.user.get_username())

    i = Item()
    i.cart = c
    i.description = request.POST['action']
    i.data = request.POST
    i.save()


    #return render(request, 'blog/post_edit.html', {'form': form})

    return HttpResponseRedirect('/orders/cart/') 

def get_workflow(request, action_id):

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
        'tab_list': tabs})


def get_cart(request):
    try:
        c = Cart.objects.get(username=request.user.username).id
    except Cart.DoesNotExist:
        c = 0

    item_list = Item.objects.order_by('-id').filter(cart=c)

    template = loader.get_template('order/cart.html')
    context = {
        'title': 'Shopping Cart',
        'item_list': item_list,
    }
    return HttpResponse(template.render(context, request))


def get_services(request):
    template = loader.get_template('order/service.html')
    action_list = Action.objects.all().order_by('service','display_seq_no')
    service_list = Service.objects.all().order_by('display_seq_no')

    for service in service_list:
        service.actions = action_list.filter(service=service)

    context = {
        'title': 'Request Service',
        'service_list': service_list,
    }
    return HttpResponse(template.render(context, request))
