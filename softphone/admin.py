from django.contrib import admin
from .models import Category, Selection, SelectionV, DuoUser
from django.urls import path
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

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


class ProcessingStatusListFilter(admin.SimpleListFilter):
    title = 'Processing Status'
    parameter_name = 'processing_status'
    def lookups(self, request, model_admin):
        return (
                ('On-Hold', _('On Hold')),
                ('Selected', _('Selected')),
                ('none', _('None')),
            )

    def queryset(self, request, queryset):
        if self.value() == 'none':
            return queryset.filter(
                processing_status=None
            )
        if self.value() == 'On-Hold':
            return queryset.filter(
                processing_status='On Hold'
            )

        if self.value() == 'Selected':
            return queryset.filter(
                processing_status='Selected'
            )
@admin.register(SelectionV)
class SelectionVAdmin(admin.ModelAdmin):
    list_display = ['service_number','subscriber','uniqname','migrate','updated_by','update_date','processing_status','zoom_login','duo_phone']
    ordering = ['-update_date']
    search_fields = ['service_number','uniqname','updated_by']
    list_filter = (ProcessingStatusListFilter,'duo_phone','zoom_login','migrate')
    #readonly_fields = SelectionV._meta.get_all_field_names()

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(DuoUser)
class DuoAdmin(admin.ModelAdmin):
    list_display = ['service_number','uniqname']
    search_fields = ['service_number','uniqname']

    def get_urls(self):
        urls = super().get_urls()

        download_url = [
            path('upload_csv/', self.upload_csv),
        ]
        return download_url + urls

    def upload_csv(self, request):
        instances = []

        for line in request.FILES['duo_file']:  
            duo = DuoUser()
            fields = line.decode('utf-8').split(',')
            duo.uniqname = fields[0].strip()[:8]
            duo.service_number = fields[1].strip().upper()[:12]
            instances.append(duo)

        DuoUser.objects.all().delete()
        DuoUser.objects.bulk_create(instances)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



