from django.contrib import admin
from .models import Category, Selection, DuoUser

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['sequence','code','label']
    ordering = ('sequence',)


@admin.register(Selection)
class SelectionAdmin(admin.ModelAdmin):
    list_display = ['service_number','subscriber','uniqname_correct','uniqname','migrate','updated_by','update_date']
    ordering = ['-update_date']
    search_fields = ['service_number','uniqname','updated_by']


@admin.register(DuoUser)
class DuoAdmin(admin.ModelAdmin):
    list_display = ['service_number','uniqname']
    search_fields = ['service_number','uniqname']