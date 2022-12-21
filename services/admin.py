from django.contrib import admin
from services.views import Azure
from .models import *

class VirtualDesktopAdmin(admin.ModelAdmin):
    model = VirtualDesktop
    list_display = ('pool_name','shortcode','admin_group')

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
    
admin.site.register(VirtualDesktop,VirtualDesktopAdmin)
