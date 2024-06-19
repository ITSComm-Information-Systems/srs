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
    

class ImageDiskInline(admin.TabularInline):
    model = ImageDisk
    ordering = ('name',)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    search_fields = ['name','owner__name']
    list_display = ['name', 'owner']
    inlines = (ImageDiskInline,)

@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    search_fields = ['name','owner__name']
    list_display = ['name', 'owner']


@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    search_fields = ['name','owner__name']
    list_display = ['name', 'owner', 'shortcode']
