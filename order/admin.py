from django.contrib import admin
from django.shortcuts import render

from .models import Service, Product, Step, Action, Feature, FeatureCategory, Restriction, Element, Constant, ProductCategory, FeatureType

class ProductAdmin(admin.ModelAdmin):
    list_display  = ['display_seq_no','label','name','category','price']
    ordering = ('display_seq_no',)

class ActionAdmin(admin.ModelAdmin):
    list_filter = ('service','type')
    list_display  = ['display_seq_no','label','service','type']
    ordering = ('display_seq_no',)
    fields = ('name',('label','cart_label'), ('display_seq_no','active'),('service','type'), 'description', ('steps','charge_types'), ('route','destination'))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        step_list = Step.objects.all().filter(action = object_id).order_by('display_seq_no')
        consts = Constant.objects.filter(action = object_id)

        for step in step_list:
            step.element_list = Element.objects.all().filter(step_id = step.id).order_by('display_seq_no')
            
        extra_context = {
            'step_list': step_list,
            'consts': consts
        }
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )


class ElementAdmin(admin.ModelAdmin):
    list_display  = ['display_seq_no','label','name','type','target']
    ordering = ('display_seq_no',)


class ServiceAdmin(admin.ModelAdmin):
    list_display  = ['display_seq_no','label','name']
    ordering = ('display_seq_no',)

class StepAdmin(admin.ModelAdmin):
    list_display = ['display_seq_no','label','name']
    ordering = ('display_seq_no',)

class FeatureAdmin(admin.ModelAdmin):
    list_filter = ('category',)
    list_display = ['display_seq_no','label']
    ordering = ('display_seq_no',)

class RestrictionAdmin(admin.ModelAdmin):
    list_display = ['display_seq_no','label','name']
    ordering = ('display_seq_no',)

class FeatureCategoryAdmin(admin.ModelAdmin):
    list_display = ['display_seq_no','label','name']
    ordering = ('display_seq_no',)

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['display_seq_no','label','name']
    ordering = ('display_seq_no',)

admin.site.register(Constant)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Element, ElementAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Step, StepAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(FeatureType)
admin.site.register(Restriction, RestrictionAdmin)
admin.site.register(FeatureCategory, FeatureCategoryAdmin)