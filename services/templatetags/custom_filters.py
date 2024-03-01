from django import template
import math

register = template.Library()

@register.filter(name='format_pool_type')
def format_pool_type(value):
    # Capitalize the first letter and replace underscores with spaces
    return value.replace('_', ' ').title()

@register.filter(name='format_cidr')
def format_cidr(value):
    return '/' + str(int(32 - math.log2(int(value))))
