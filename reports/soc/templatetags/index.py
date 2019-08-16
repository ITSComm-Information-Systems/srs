from django import template
register = template.Library()

@register.filter
def divide(a, b)
	return a/b

@register.filter
def currency(money):
	return '${:,.2f}'.format(money)