from django import template
from apps.bom.models import Technician

register = template.Library()

@register.filter(name='in_group')
def in_group(user, group_name):
    engineers = Technician.objects.filter(wo_group_code=group_name).values_list('user_name', flat=True)
    return user.username in engineers
