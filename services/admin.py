from django.contrib import admin
from .models import AWSAccount


@admin.register(AWSAccount)
class AWSAccountAdmin(admin.ModelAdmin):
    pass