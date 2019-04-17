from django.contrib import admin
from django.shortcuts import render

from .models import Service, Product, Step, Action, Feature, FeatureCategory, Restriction, Element

class ProductAdmin(admin.ModelAdmin):
    list_display  = ['display_seq_no','name','description']

class ActionAdmin(admin.ModelAdmin):
    list_filter = ('service','type')
    list_display  = ['display_seq_no','name','service','type']
    fields = ('name', ('display_seq_no','active'),('service','type'), 'steps', ('route','destination'))
    step_list = Step.objects.all().filter(action = 1).order_by('display_seq_no')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        step_list = Step.objects.all().filter(action = object_id).order_by('display_seq_no')

        for step in step_list:
            step.element_list = Element.objects.all().filter(step_id = step.id).order_by('display_seq_no')
            
        extra_context = {
            'step_list': step_list,
        }
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )


class ElementAdmin(admin.ModelAdmin):
    list_display  = ['step','name','type','target','display_seq_no','label']


class ServiceAdmin(admin.ModelAdmin):
    list_display  = ['name','display_seq_no','active']

class StepAdmin(admin.ModelAdmin):
    list_display = ['name','display_seq_no','custom_form']

class FeatureAdmin(admin.ModelAdmin):
    list_filter = ('category',)
    list_display = ['display_seq_no','name','description']

class RestrictionAdmin(admin.ModelAdmin):
    list_display = ['display_seq_no','name']

class FeatureCategoryAdmin(admin.ModelAdmin):
    list_display = ['name','display_seq_no']

admin.site.register(Element, ElementAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Step, StepAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(Restriction, RestrictionAdmin)
admin.site.register(FeatureCategory, FeatureCategoryAdmin)