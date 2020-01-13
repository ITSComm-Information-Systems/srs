from pages.models import Page
from order.models import ServiceGroup
import os

def menu(request):
    background_color = os.getenv('BACKGROUND_COLOR', 'green')

    service_groups = ServiceGroup.objects.filter(active=True).order_by('display_seq_no')

    return {
        'service_groups': service_groups,
        'background_color': background_color,
    }