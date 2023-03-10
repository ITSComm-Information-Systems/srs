from django import template
register = template.Library()

@register.filter
def options(descr):
	return descr.split(' ', 1)[1]

@register.filter
def protocol(descr):
    return descr.split(' ', 1)[0]

@register.filter
def currency(money):
	return '${:,.2f}'.format(money)