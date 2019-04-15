from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from order.forms import *

from .models import Cart, Product, Action, Service, Step, Element

def add_to_cart(request):
    if request.method == "POST":
        print(request.POST)
        form = ChartfieldForm(request.POST)

        if form.is_valid():
            print(form.cleaned_data['occ'])

            c, created = Cart.objects.get_or_create(number='Not Submitted', description='Order',username=request.user.get_username())

            i = Item()
            i.cart = c
            i.action = 'Add a new phone'
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
        tab.step = 'step' + str(index)

        if tab.custom_form == '':
            f = forms.Form()
            f.template = 'order/dynamic_form.html'
            element_list = Element.objects.all().filter(step_id = tab.id).order_by('display_seq_no')

            for element in element_list:
                if element.type == 'YN':
                    field = forms.ChoiceField(label=element.label, widget=forms.RadioSelect, choices=(('Y', 'Yes',), ('N', 'No',)))
                elif element.type == 'ST':
                    field = forms.CharField(label=element.label)
                else:
                    field = forms.IntegerField(label=element.label)

                f.fields.update({element.target: field})

            tab.form = f
        else:
            tab.form = globals()[tab.custom_form]

    return render(request, 'order/workflow.html', 
        {'title': action,
        'tab_list': tabs})


def load_actions(request):
    service = request.GET.get('service')
    service_id = Service.objects.get(name=service)
    actions = Action.objects.filter(service=service_id)
    return render(request, 'order/workflow_actions.html', {'actions': actions})

def cart(request):
    #item_list = Item.objects.order_by('-id')
    item_list = ['one','two']
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
