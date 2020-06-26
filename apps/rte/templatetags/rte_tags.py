from django.template import Library

register = Library()

@register.filter(name='is_member')
def is_member(user, group_name):
	return user.groups.filter(name=group_name).exists()
