from pages.models import Page
from order.models import ServiceGroup
from django.conf import settings
import os

def menu(request):
    background_color = os.getenv('BACKGROUND_COLOR', 'grey')

    if settings.DEBUG:
        connections = settings.DATABASES['default']['NAME'] + '\n' + settings.DATABASES['pinnacle']['NAME']
    else:
        connections = ''

    service_groups = ServiceGroup.objects.filter(active=True).order_by('display_seq_no')

    return {
        'service_groups': service_groups,
        'background_color': background_color,
        'connections': connections
    }