from pages.models import Page
from order.models import Service, Action

def menu(request):
    help_menu = Page.objects.filter(display_seq_no__gt=0).order_by('display_seq_no')
    service_menu = Service.objects.filter(display_seq_no__gt=0).order_by('display_seq_no')

    for item in service_menu:
        item.subitems = Action.objects.filter(service=item).order_by('display_seq_no')


    return {
        'help_menu': help_menu,
        'service_menu': service_menu
    }