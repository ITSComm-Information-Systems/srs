from django.contrib import admin

from .models import Service, Action, Attribute

class ServiceAdmin(admin.ModelAdmin):
    list_display  = ['name','description']


class ActionAdmin(admin.ModelAdmin):
    list_display  = ['service', 'name','description']


class AttributeAdmin(admin.ModelAdmin):
    list_display  = ['name','description']


admin.site.register(Service, ServiceAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Attribute, AttributeAdmin)
