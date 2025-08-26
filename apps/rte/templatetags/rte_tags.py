from django.template import Library

register = Library()

@register.filter(name='is_member')
def is_member(user, group_name):
	return user.groups.filter(name=group_name).exists()

@register.filter(name='dict_key')
def dict_key(d, key):
    if isinstance(d, dict):
        return d.get(key, {})
    return {}