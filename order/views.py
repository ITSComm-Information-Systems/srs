from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from order.forms import forms

from .models import Cart, Item, Product, Action, Service, Step

from .forms import WorkflowForm, LocationForm, EquipmentForm, ReviewForm, ProductForm, FeaturesForm, PhoneForm

def add_to_cart(request):
    print('added to cart')

    return HttpResponseRedirect('/orders/cart/') 

def get_workflow(request, action_id):
    form_list = []
    tab_list = []

    tabs = Step.objects.filter(action = action_id).order_by('display_seq_no')

    for tab in tabs:
        tab_list.append(tab.label)
        form_list.append(globals()[tab.name]) # Get form class name dynamicaly

    return render(request, 'order/workflow.html', 
        {'title': 'Place Order',
        'tab_list': tab_list,
        'form_list': form_list})


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
