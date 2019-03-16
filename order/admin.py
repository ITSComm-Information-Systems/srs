from django.contrib import admin


from .models import Service, Action, Product, Workflow, Step

class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name','display_seq_no','description','picture']

class ActionAdmin(admin.ModelAdmin):
    list_display  = ['name','display_seq_no']

class ServiceAdmin(admin.ModelAdmin):
    list_display  = ['name','display_seq_no','active','workflow']

class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name']

class StepAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Service, ServiceAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(Step, StepAdmin)