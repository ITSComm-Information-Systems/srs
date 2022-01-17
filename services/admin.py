from django.contrib import admin

from services.views import Azure
from .models import *


class CloudAdmin(admin.ModelAdmin):
    list_display = ('account_id','billing_contact','shortcode')


@admin.register(AWS)
class AWSAccountAdmin(admin.ModelAdmin):
    list_display = ('account_id','owner','billing_contact','shortcode','created_date')
    

@admin.register(GCP)
class GCPAdmin(admin.ModelAdmin):
    list_display = ('account_id','billing_contact','shortcode')
    

@admin.register(Azure)
class AzureAdmin(CloudAdmin):
    pass
