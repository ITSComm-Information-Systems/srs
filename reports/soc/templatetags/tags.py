from django import template
register = template.Library()

@register.simple_tag
def divide(a, b):
	return '{:,.2f}'.format(float(a / b))

@register.filter
def currency(money):
	credit = False
	if money < 0:
		credit = True
		money = abs(money)
	if credit:
		return '-${:,.2f}'.format(money)
	else:
		return '${:,.2f}'.format(money)