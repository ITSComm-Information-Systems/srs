from django.contrib import admin
from services.views import Azure
from .models import *


class CloudAdmin(admin.ModelAdmin):
    list_display = ('account_id','owner','billing_contact','shortcode','created_date')


@admin.register(AWS)
class AWSAccountAdmin(CloudAdmin):
    pass


@admin.register(Azure)
class AzureAdmin(CloudAdmin):
    pass


@admin.register(GCP)
class GCPAdmin(CloudAdmin):
    list_display = ('project_id','account_id','owner','billing_contact','shortcode','created_date')


class GCPInline(admin.TabularInline):
    model = GCP
    fields = ['status','project_id','owner']


@admin.register(GCPAccount)
class GCPAccountAdmin(CloudAdmin):
    inlines = [GCPInline]

@admin.register(CloudImage)
class CloudImageAdmin(admin.ModelAdmin):
    list_display = ('account_id','owner','shortcode','created_date')
    readonly_fields = ('cpu','cpu_cost','memory','memory_cost','storage','storage_cost','gpu','gpu_cost','total')
    fieldsets = (
        (None, {
            'fields': ('status','owner','shortcode'),
        }),
        ('Resource Details', {
            'fields': ('cpu','cpu_cost','memory','memory_cost','storage','storage_cost','gpu','gpu_cost','total'),
        }),
    )


@admin.register(CloudDesktop)
class CloudDesktopAdmin(admin.ModelAdmin):
    list_display = ('account_id','owner','shortcode','created_date')
    readonly_fields = ('pool_maximum','pool_cost')
    fieldsets = (
        (None, {
            'fields': ('status','owner'),
        }),
        (None, {
            'fields': ('pool_maximum', 'pool_cost', 'ad_access_groups','sla','persistent_vm'),
        }),
    )

