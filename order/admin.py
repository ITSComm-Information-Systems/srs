import csv, json

from django.utils.html import format_html
from django import forms
from django.core.exceptions import ValidationError
from project.integrations import MCommunity
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.urls import path
from project.models import Choice

from .models import Service, ServiceGroup, Product, Step, Action, Feature, FeatureCategory, Restriction, Element, Constant, ProductCategory, FeatureType, StorageInstance, StorageHost, StorageRate, BackupDomain, BackupNode, ArcInstance, ArcHost, ArcBilling, LDAPGroup, Ticket, Item, Server, ServerDisk, Database, LDAPGroupMember

class ProductAdmin(admin.ModelAdmin):
    list_display  = ['display_seq_no','label','name','category','price']
    ordering = ('display_seq_no',)


class ActionAdmin(admin.ModelAdmin):
    list_filter = ('service','type')
    list_display  = ['display_seq_no','label','service','type']
    ordering = ('service','display_seq_no',)
    fields = ('name',('label','use_cart','cart_label'), ('display_seq_no','active','use_ajax'),('service','type'), 'description', ('steps','charge_types'), ('route','destination'), 'override')


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
    
        override = json.dumps(action.override, indent=4)

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


class ServiceInstanceAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()

        download_url = [
            path('download_csv/', self.download_csv),
        ]
        return download_url + urls

    def download_csv(self, request):

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="full_list.csv"'

        writer = csv.writer(response)
        fields = self.model._meta.fields

        choice_related = []
        row = []
        for field in fields:
            row.append(field.name)
            if field.related_model:
                choice_related.append(field.name)

        writer.writerow(row)
        instances = self.model.objects.all().select_related(*choice_related)
        if not request.GET.get('admin', '') or not request.user.is_staff:   # When called from order page just show user's data.
            groups = list(LDAPGroupMember.objects.filter(username= request.user).values_list('ldap_group_id'))
            instances = instances.filter(owner__in=groups, in_service=True).order_by('name').select_related('owner')

        for instance in list(instances):
            row = []
            for field in fields:
                if self.model == ArcInstance and field.name == 'shortcode':
                    shortcode = ''
                    for sc in instance.get_shortcodes():
                        shortcode = shortcode + f'{sc.size}TB to {sc.shortcode},'

                    row.append(shortcode)
                else:
                    row.append(getattr(instance,field.name))

            writer.writerow(row)

        return response

def user_has_permission(request, obj=None):
    if request.user.has_perm('order.change_server'):
        return True
    elif request.user.has_perm('order.change_database'):
        if obj:
            if obj.admin_group_id == Database.MDB_ADMIN_GROUP:
                return True
    return False    

class ServerDiskInline(admin.TabularInline):
    model = ServerDisk
    ##ordering = ('controller','device') 
    ordering = ('name',)

    #def has_add_permission(self, request, obj=None):
    #    return user_has_permission(request, obj)

    #def has_change_permission(self, request, obj=None):
    #    return user_has_permission(request, obj)
        

@admin.register(Database)
class DatabaseAdmin(ServiceInstanceAdmin):
    list_display = ['name', 'owner','type', 'shared']
    list_filter = ('in_service','type')
    ordering = ('name',)
    readonly_fields = ('legacy_data','server','shared')
    search_fields = ['name','owner__name']
    autocomplete_fields = ['owner']
    list_select_related = ['owner','type','server']
    
    fieldsets = (
        (None, {
            'fields': (('name', 'in_service'), 'owner', 'shortcode', 'type', 'url', 'on_call',
            ('support_email','support_phone'),
            ('shared', 'size'),
            'purpose'
            )
        }),
        ('Legacy Data', {
            'classes': ('collapse',),
            'fields': ('legacy_data',),
        }),
    )

    def change_view(self, request, object_id, form_url='', extra_context=None):

        db = Database.objects.get(id=object_id)
        if db.server:
            extra_context = {'server': Server.objects.get(id=db.server_id)}
        else:
            extra_context = {}

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

@admin.register(Server)
class ServerAdmin(ServiceInstanceAdmin):
    list_display = ['name', 'owner', 'os']
    list_filter = ('in_service','managed', 'database_type')
    ordering = ('name',)
    search_fields = ['name','owner__name']
    autocomplete_fields = ['owner','admin_group']
    list_select_related = ['owner','os']
    inlines = [ServerDiskInline,]

    readonly_fields = ('created_date','total_cost','total_disk_size')

    fieldsets = (
        (None, {
            'fields': (('name', 'in_service','created_date'), 'owner', ('admin_group','database_type'), 'shortcode', ('os','cpu','ram'),
                        ('replicated','backup','backup_time','public_facing','production'),
                        ('on_call', 'support_email', 'support_phone'),
                        ('cname',),

                        ('regulated_data','non_regulated_data'),
                        'managed'
                        ),
        }),
        ('Managed', {
            'classes': ('managed-section',),
            'fields': (('patch_day','patch_time'),
                    ('reboot_day', 'reboot_time'),),
        }),
        (None, {
            'fields': (('total_disk_size','total_cost'),),
        }),
    )

    class Media:
        js = ('order/js/admin_server.js',)

    #def has_change_permission(self, request, obj=None):
    #    return user_has_permission(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):

        instance = self.model.objects.get(id=object_id)
 
        extra_context = {
            'ticket_list': instance.get_tickets() 
        }
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    title = 'Select an instance'
    list_display = ['ticket','service','volume','status',]
    ordering = ('-ticket_id',)

    def ticket(self,obj): 
        return format_html(f"<a target=”_blank” href='{obj.ticket_link}'>{obj.ticket_id}</a>")

    def volume(self,obj): 
        if obj.instance_id:
            return format_html(f"<a href='/admin/order/arcinstance/{obj.instance.id }'>{obj.instance}</a>")
        else:
            return '-'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        item = Item.objects.get(id=object_id)
        instance_id = item.data['instance_id']
        return HttpResponseRedirect(f'/admin/order/arcinstance/{instance_id}/change/')


@admin.register(LDAPGroup)
class LDAPGroupAdmin(admin.ModelAdmin):
    search_fields = ['name']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/refresh_groupn/',
                self.admin_site.admin_view(self.refresh_group),
                name='refresh_group',
            ),
        ]
        return custom_urls + urls

    def refresh_group(self, request, object_id):
        # Your custom logic here
        group = LDAPGroup.objects.get(id=object_id)
        group.update_membership()

        self.message_user(request, "Group Refreshed!")
        return HttpResponseRedirect(f"../")

    def change_view(self, request, object_id, form_url='', extra_context=None):
        user_list = LDAPGroupMember.objects.filter(ldap_group_id=object_id).order_by('username')

        return super().change_view(
            request, object_id, form_url, extra_context={'user_list': user_list},
        )


class VolumeAdmin(ServiceInstanceAdmin):
    ordering = ('name',)
    search_fields = ['name','owner__name']
    list_filter = ('type',('service', admin.RelatedOnlyFieldListFilter),)
    child_record = 'TBD'
    service_list = []
    autocomplete_fields = ['owner']

    def get_urls(self):
        urls = super().get_urls()

        fulfill_url = [
            path('fulfill_order/', self.fulfill_order),
        ]

        return fulfill_url + urls

    def fulfill_order(self, request):
        item = Item.objects.get(external_reference_id=request.POST['ticket'])
        instance_id = item.data['instance_id']

        if request.POST['action'] == 'Cancel':
            item.data['fulfill'] = 'Cancelled'
        else:
            item.update_database({'record': 'ArcInstance'})
            item.data['fulfill'] = 'Complete'
        
        item.save()

        return HttpResponseRedirect(f'/admin/order/arcinstance/{instance_id}/change/')

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.service_id = obj.service_id
            self.type = obj.type
        else:
            type = request.GET.get('type', '')
            if type:
                self.type = type
                self.service_id = 7
                
        return super(VolumeAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "rate":
            try:
                kwargs["queryset"] = StorageRate.objects.filter(service_id=self.service_id,type=self.type)
            except:
                kwargs["queryset"] = StorageRate.objects.filter(service_id__in=self.service_list)
        if db_field.name == "service":
            kwargs["queryset"] = Service.objects.filter(id__in=self.service_list)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def changelist_view(self, request, extra_context=None):

        self.list_display = ['name','type','owner','size','rate','total_cost']     

        q = request.META['QUERY_STRING']

        if q == 'type__exact=NFS':
            self.list_display.append('uid')
        elif q == 'type__exact=CIFS':
            self.list_display.append('ad_group')
         
        return super().changelist_view(
            request, extra_context=extra_context,
        )

    def change_view(self, request, object_id, form_url='', extra_context=None):

        instance = self.model.objects.get(id=object_id)
        #if instance.type == 'CIFS':
        #    self.exclude = ['flux','uid']

        #else:
            #print(self.child_key)

            #host_list = instance.get_hosts()

            #if self.child_record == ArcHost:
            #    host_list = self.child_record.objects.all().filter(arc_instance_id=object_id)
            #else:
            #    host_list = self.child_record.objects.all().filter(storage_instance_id=object_id)
 
        extra_context = {
            'host_list': instance.get_hosts(),
            'shortcode_list': instance.get_shortcodes(),
            'ticket_list': instance.get_tickets() 
        }
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )


@admin.register(ArcInstance)
class ArcInstanceAdmin(VolumeAdmin):
    readonly_fields = ['created_date']
    child_record = ArcHost
    child_key = 'arc_instance_id'
    service_list = [9,10,11]
    list_select_related = ['owner','rate']
    fieldsets = (
        (None, {'fields': ('service', 'name','owner',('type','multi_protocol','ad_group'),'rate','size',('uid','nfs_group_id'),'research_computing_package','college','amount_used','created_date','sensitive_regulated')
        }),
        ('Regulated/Sensitive', {'fields':(('armis','globus_phi'),)
        }),
        ('No Regulated/Sensitive', {'fields':(('lighthouse','globus','thunder_x','great_lakes'),)
        })
    )

    class Media:
        js = ('order/js/admin_arc.js',)

    def bak_formfield_for_foreignkey(self, db_field, request, **kwargs):
        self.service_id = None
        self.type = None
        if db_field.name == "rate":
            kwargs["queryset"] = StorageRate.objects.filter(service_id__in=self.service_list)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
            #print(self.service_id, self.service_list)
        #elif db_field.name == "service":
        #    kwargs["queryset"] = Service.objects.filter(id__in=self.service_list)
        else:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(StorageInstance)
class StorageInstanceAdmin(VolumeAdmin):
    child_record = StorageHost
    child_key = 'storage_instance_id'
    service_list = [7]
    list_select_related = ['owner','rate']
    exclude = ['owner_name', 'owner_bak']


@admin.register(ArcBilling)
class ArcBillingAdmin(admin.ModelAdmin):
    list_display = ['arc_instance','shortcode','size']
    pass

@admin.register(ArcHost)
class ArcHostAdmin(admin.ModelAdmin):
    list_display = ['name','arc_instance']
    search_fields = ['name']

@admin.register(StorageHost)
class StorageHostAdmin(admin.ModelAdmin):
    list_display = ['name','storage_instance']
    search_fields = ['name']

class StorageRateAdmin(admin.ModelAdmin):
    list_display = ['display_seq_no','name','label','type','rate','service']
    ordering = ('service','display_seq_no',)
    list_filter = ('service',)


class BackupDomainAdmin(ServiceInstanceAdmin):
    list_display = ['name','owner','shortcode','size']

    def change_view(self, request, object_id, form_url='', extra_context=None):

        node_list = BackupNode.objects.all().filter(backup_domain_id=object_id)
                
        extra_context = {
            'node_list': node_list,
        }

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

class BackupNodeAdmin(admin.ModelAdmin):
    list_display = ['name','backup_domain']
    search_fields = ['name']


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

#admin.site.register(StorageHost)
admin.site.register(StorageRate, StorageRateAdmin)

admin.site.register(BackupDomain, BackupDomainAdmin)
admin.site.register(BackupNode, BackupNodeAdmin)