from django.http import HttpResponse
from django.template import loader

from .models import Cart, Item

def index(request):
    item_list = Item.objects.order_by('-id')
    template = loader.get_template('order/index.html')
    context = {
        'item_list': item_list,
    }
    return HttpResponse(template.render(context, request))