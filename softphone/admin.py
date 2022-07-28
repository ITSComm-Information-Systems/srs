from django.contrib import admin
from .models import Category, Selection, SelectionV, DuoUser

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['sequence','code','label']
    ordering = ('sequence',)


@admin.register(Selection)
class SelectionAdmin(admin.ModelAdmin):
    list_display = ['service_number','subscriber','uniqname','migrate','updated_by','update_date','processing_status']
    ordering = ['-update_date']
    search_fields = ['service_number','uniqname','updated_by']
    list_filter = ['processing_status']


@admin.register(SelectionV)
class SelectionVAdmin(admin.ModelAdmin):
    list_display = ['service_number','subscriber','uniqname','migrate','updated_by','update_date','processing_status','zoom_login','duo_phone']
    ordering = ['-update_date']
    search_fields = ['service_number','uniqname','updated_by']
    list_filter = ['processing_status','duo_phone','zoom_login']
    #readonly_fields = SelectionV._meta.get_all_field_names()

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(DuoUser)
class DuoAdmin(admin.ModelAdmin):
    list_display = ['service_number','uniqname']
    search_fields = ['service_number','uniqname']