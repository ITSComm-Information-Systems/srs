from django import template
register = template.Library()

@register.filter
def index(list, i):
    return list[int(i)]

@register.filter
def currency(money):
	return '${:,.2f}'.format(money)