from django.contrib import admin
from .models import Category, Selection

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['sequence','code','label']
    ordering = ('sequence',)


@admin.register(Selection)
class SelectionAdmin(admin.ModelAdmin):
    list_display = ['subscriber','uniqname_correct','uniqname','migrate','category','updated_by','update_date']
