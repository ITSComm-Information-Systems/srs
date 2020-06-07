import csv, json

from django.http import HttpResponse
from django.template import loader
from django.contrib import admin
from django.shortcuts import render
from django.urls import path


from .models import Service, ServiceGroup, Product, Step, Action, Feature, FeatureCategory, Restriction, Element, Constant, ProductCategory, FeatureType, StorageInstance, StorageHost, StorageRate, BackupDomain, BackupNode

class ProductAdmin(admin.ModelAdmin):
    list_display  = ['display_seq_no','label','name','category','price']
    ordering = ('display_seq_no',)


class ActionAdmin(admin.ModelAdmin):
    list_filter = ('service','type')
    list_display  = ['display_seq_no','label','service','type']
    ordering = ('service','display_seq_no',)
    fields = ('name',('label','use_cart','cart_label'), ('display_seq_no','active','use_ajax'),('service','type'), 'description', ('steps','charge_types'), ('route','destination'))


    def get_urls(self):
        urls = super().get_urls()

        override_url = [
            path('<int:action_id>/override/', self.override_view),
        ]
        return override_url + urls


    def save_model(self, request, obj, form, change):
        tab_list = Step.objects.filter(action=obj)
        show_fields = request.POST.getlist('show_field')
        unchecked_fields = list(Element.objects.filter(step__in=tab_list).exclude(name__in=show_fields).values_list('name', flat=True))

        if obj.override:
            obj.override['hide'] = unchecked_fields
        else:
            obj.override = {"hide": unchecked_fields}

        super().save_model(request, obj, form, change)

    def override_view(self, request, action_id):
        #response = HttpResponse(content_type='text/csv')
        template = loader.get_template('admin/order/action/override_form.html')
        #template = loader.get_template('admin/add_label_form.html')
        context = {
            'title': 'Order Summary',
            #'order': order,
            #'item_list': item_list
        }
        return HttpResponse(template.render(context, request))
        #return response

    def change_view(self, request, object_id, form_url='', extra_context=None):
        step_list = Step.objects.all().filter(action = object_id).order_by('display_seq_no')
        consts = Constant.objects.filter(action = object_id)
        action = Action.objects.get(id=object_id)
        hidden_fields = action.get_hidden_fields()

        for step in step_list:
            step.element_list = Element.objects.all().filter(step_id = step.id).order_by('display_seq_no')

            for element in step.element_list:
                if element.name not in hidden_fields:
                    element.checked = True
    
        override = 'x'
        #p,arsed = json.loads(action.override)
        #,override = json.dumps(parsed, indent=4)

        extra_context = {
            'step_list': step_list,
            'consts': consts,
            'override': override
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
    search_fields = ['name','owner__name']
    list_filter = ('type','service')

    def get_urls(self):
        urls = super().get_urls()

        download_url = [
            path('download_csv/', self.download_csv),
        ]
        return download_url + urls

    def download_csv(self, request):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="mistorage.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Owner', 'Size', 'Type','Created Date','Shortcode','Deptid','UID','Flux Flag','Rate','Total Cost'])

        instance_list = StorageInstance.objects.all().select_related()
        for i in instance_list:
            writer.writerow([i.name,i.owner,i.size,i.type,i.created_date,i.shortcode,i.deptid,i.uid,i.flux,i.rate,i.total_cost ])

        return response

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
    list_display = ['display_seq_no','name','label','type','rate','service']
    ordering = ('service','display_seq_no',)
    list_filter = ('service',)


class BackupDomainAdmin(admin.ModelAdmin):
    list_display = ['name','owner','shortcode','total_cost']

    def change_view(self, request, object_id, form_url='', extra_context=None):

        node_list = BackupNode.objects.all().filter(backup_domain_id=object_id)
                
        extra_context = {
            'node_list': node_list,
        }

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )


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

admin.site.register(BackupDomain, BackupDomainAdmin)
admin.site.register(BackupNode)