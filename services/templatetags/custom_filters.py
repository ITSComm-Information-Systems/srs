from django import template

register = template.Library()

@register.filter(name='format_string')
def format_string(value):
    # Capitalize the first letter and replace underscores with spaces
    return value.capitalize().replace('_', ' ')