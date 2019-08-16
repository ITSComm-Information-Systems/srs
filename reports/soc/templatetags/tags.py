from django import template
register = template.Library()

@register.simple_tag
def divide(a, b):
	return '{:,.2f}'.format(float(a / b))

@register.filter
def currency(money):
	return '${:,.2f}'.format(money)