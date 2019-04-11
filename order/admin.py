from django.contrib import admin
from django.shortcuts import render

from .models import Service, Product, Step, Action, Feature, FeatureCategory, Restriction

class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name','display_seq_no','description']

class ActionAdmin(admin.ModelAdmin):
    list_filter = ('service','type')
    list_display  = ['display_seq_no','name','service','type']


class ServiceAdmin(admin.ModelAdmin):
    list_display  = ['name','display_seq_no','active']

class StepAdmin(admin.ModelAdmin):
    list_display = ['name','label','display_seq_no']

class FeatureAdmin(admin.ModelAdmin):
    list_filter = ('category',)
    list_display = ['display_seq_no','name','description']

class RestrictionAdmin(admin.ModelAdmin):
    list_display = ['display_seq_no','name']

class FeatureCategoryAdmin(admin.ModelAdmin):
    list_display = ['name','display_seq_no']


admin.site.register(Service, ServiceAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Step, StepAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(Restriction, RestrictionAdmin)
admin.site.register(FeatureCategory, FeatureCategoryAdmin)