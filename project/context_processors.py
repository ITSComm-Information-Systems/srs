from pages.models import Page
from order.models import ServiceGroup
from oscauth.models import LDAPGroupMember
from django.conf import settings
import os

def menu(request):
    background_color = os.getenv('BACKGROUND_COLOR', 'grey')

    if settings.DEBUG:
        connections = settings.DATABASES['default']['NAME'] + '\n' + settings.DATABASES['pinnacle']['NAME']
    else:
        connections = ''

    service_groups = ServiceGroup.objects.filter(active=True).order_by('display_seq_no')
    is_mssql_dba = False
    if request.user.is_authenticated:
        is_mssql_dba = LDAPGroupMember.objects.filter(
            username=request.user.username,
            ldap_group__name__iexact='its mssqldba',
        ).exists()

    return {
        'service_groups': service_groups,
        'is_mssql_dba': is_mssql_dba,
        'background_color': background_color,
        'connections': connections
    }