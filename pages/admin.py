from django.contrib import admin
from .models import Page


#class that determines how pages appear to admin
class PageAdmin(admin.ModelAdmin):
   list_display = ('permalink','title','display_seq_no','update_date')
   ordering = ('display_seq_no','title',)
   search_fields = ('title',)

# Register your models here.
admin.site.register(Page,PageAdmin)