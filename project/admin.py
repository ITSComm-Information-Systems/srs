from django.contrib import admin
from .models import Test

class TestAdmin(admin.ModelAdmin):
    list_display = ('user','url','result')
    ordering = ('user','url')
    search_fields = ('url',)

admin.site.register(Test, TestAdmin)