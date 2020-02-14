from django.contrib import admin
from django.shortcuts import render

from .models import Service, ServiceGroup, Product, Step, Action, Feature, FeatureCategory, Restriction, Element, Constant, ProductCategory, FeatureType, StorageInstance, StorageHost, StorageRate

class ProductAdmin(admin.ModelAdmin):
    list_display  = ['display_seq_no','label','name','category','price']
    ordering = ('display_seq_no',)


class ActionAdmin(admin.ModelAdmin):
    list_filter = ('service','type')
    list_display  = ['display_seq_no','label','service','type']
    ordering = ('display_seq_no',)
    fields = ('name',('label','use_cart','cart_label'), ('display_seq_no','active'),('service','type'), 'description', ('steps','charge_types'), ('route','destination'))

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


class ServiceGroupAdmin(admin.ModelAdmin):
    list_display  = ['display_seq_no','label','name']
    ordering = ('display_seq_no',)


class ServiceAdmin(admin.ModelAdmin):
    list_display  = ['display_seq_no','label','name']
    ordering = ('display_seq_no',)


class StepAdmin(admin.ModelAdmin):
    list_display = ['display_seq_no','label','name']
    ordering = ('display_seq_no',)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        element_list = Element.objects.all().filter(step_id = object_id).order_by('display_seq_no')
            
        extra_context = {
            'element_list': element_list,
        }
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )


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


class StorageInstanceAdmin(admin.ModelAdmin):
    ordering = ('name',)
    search_fields = ['name','owner']
    list_filter = ('type',)

    def changelist_view(self, request, extra_context=None):

        q = request.META['QUERY_STRING']

        if q == 'type__exact=NFS':
            self.list_display = ['name','uid','flux','size','rate','owner','created_date']
        elif q == 'type__exact=CIFS':
            self.list_display = ['name','size','rate','owner', 'created_date']
        else:
            self.list_display = ['name','type','size','rate','owner', 'created_date']            

        return super().changelist_view(
            request, extra_context=extra_context,
        )


    def change_view(self, request, object_id, form_url='', extra_context=None):

        instance = StorageInstance.objects.get(id=object_id)

        if instance.type == 'CIFS':
            self.exclude = ['flux','uid']

        else:
            host_list = StorageHost.objects.all().filter(storage_instance_id=object_id)
                
            extra_context = {
                'host_list': host_list,
            }
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )



class StorageRateAdmin(admin.ModelAdmin):
    list_display = ['display_seq_no','name','label','type','rate']
    ordering = ('display_seq_no',)


admin.site.register(Constant)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Element, ElementAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceGroup, ServiceGroupAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Step, StepAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(FeatureType)
admin.site.register(Restriction, RestrictionAdmin)
admin.site.register(FeatureCategory, FeatureCategoryAdmin)

admin.site.register(StorageInstance, StorageInstanceAdmin)
admin.site.register(StorageHost)
admin.site.register(StorageRate, StorageRateAdmin)