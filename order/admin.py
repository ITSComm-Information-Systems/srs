from django.contrib import admin


from .models import Service, Product, Step, Action, Feature

class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name','display_seq_no','description','picture']

class ActionAdmin(admin.ModelAdmin):
    list_display  = ['service','name','display_seq_no']
    fieldsets = (
        (None, {
           'fields': ('service', 'name', 'display_seq_no')
        }),
        ('Options', {
            'fields': (('steps','products','features'),('route','destination')),
        }),
    )

class ServiceAdmin(admin.ModelAdmin):
    list_display  = ['name','display_seq_no','active']

class StepAdmin(admin.ModelAdmin):
    list_display = ['name','label','display_seq_no']

class FeatureAdmin(admin.ModelAdmin):
    list_display = ['name','display_seq_no']

admin.site.register(Service, ServiceAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Step, StepAdmin)
admin.site.register(Feature, FeatureAdmin)