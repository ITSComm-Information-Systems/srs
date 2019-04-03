from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from order.forms import *

from .models import Cart, Item, Product, Action, Service, Step

#from .forms import WorkflowForm, LocationForm, EquipmentForm, ReviewForm, ProductForm, FeaturesForm, PhoneForm

def add_to_cart(request):
    if request.method == "POST":
        print(request.POST)
        form = ChartfieldForm(request.POST)

        if form.is_valid():
            print(form.cleaned_data['occ'])

            c = Cart()
            c.number = 1
            c.description = 'New office'
            c.save()

            i = Item()
            i.cart = c
            i.service = 'Phone'
            i.service_action = 'Add'
            i.service_detail ='Add Phone'
            i.status = 'Start'
            i.save()
        else:
            print('bad form')
    else:
        form = PostForm()

    #return render(request, 'blog/post_edit.html', {'form': form})

    return HttpResponseRedirect('/orders/cart/') 

def get_workflow(request, action_id):

    tabs = Step.objects.filter(action = action_id).order_by('display_seq_no')
    action = Action.objects.get(id=action_id)

    for index, tab in enumerate(tabs, start=1):
        tab.form = globals()[tab.name]
        tab.step = 'step' + str(index)

    return render(request, 'order/workflow.html', 
        {'title': action,
        'tab_list': tabs})


def load_actions(request):
    service = request.GET.get('service')
    service_id = Service.objects.get(name=service)
    print(service_id)
    actions = Action.objects.filter(service=service_id)
    print(actions)
    #actions = Action.objects.all()
    print(actions)
    return render(request, 'order/workflow_actions.html', {'actions': actions})

def cart(request):
    item_list = Item.objects.order_by('-id')
    print(request.build_absolute_uri())
    template = loader.get_template('order/cart.html')
    context = {
        'title': 'Shopping Cart',
        'item_list': item_list,
    }
    return HttpResponse(template.render(context, request))


def get_services(request):
    #item_list = Item.objects.order_by('-id')
    template = loader.get_template('order/service.html')
    action_list = Action.objects.all().order_by('display_seq_no')
    service_list = Service.objects.all().order_by('display_seq_no')
    context = {
        'title': 'Request Service',
        'action_list': action_list,
        'service_list': service_list,
    }
    return HttpResponse(template.render(context, request))
