from django.contrib import admin
from django import forms
from .models import Category, Selection, SelectionV, DuoUser, Ambassador
from django.urls import path
from django.http import HttpResponseRedirect
from .forms import migrate_choices

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['sequence','code','label']
    ordering = ('sequence',)

processing_choices = (
    ('','---'),
    ('Selected','Selected'),
    ('Completed','Completed'),
    ('On Hold','On Hold')
    )

class SelectionForm(forms.ModelForm):
    migrate = forms.ChoiceField(choices = migrate_choices)
    processing_status = forms.ChoiceField(choices = processing_choices, required=False)

    class Meta:
        model = Selection
        exclude = []


class ZoomListFilter(admin.SimpleListFilter):
    title = 'Zoom Login'
    parameter_name = 'zoom'

    def lookups(self, request, model_admin):
        return (('YES', 'Yes'), ('NO', 'No'),)

    def queryset(self, request, queryset):
        if self.value() == 'YES':
            subscriber_list = list(SelectionV.objects.filter(zoom_login='Y').values_list('subscriber', flat=True))
            return queryset.filter(subscriber__in=subscriber_list)
        if self.value() == 'NO':
            subscriber_list = list(SelectionV.objects.filter(zoom_login='N').values_list('subscriber', flat=True))
            return queryset.filter(subscriber__in=subscriber_list)
 


class DuoListFilter(admin.SimpleListFilter):
    title = 'Duo User'
    parameter_name = 'duo'

    def lookups(self, request, model_admin):
        return (('True', True), ('False', False))

    def queryset(self, request, queryset):
        service_number_list = list(DuoUser.objects.values_list('service_number', flat=True))
        if self.value() == 'True':
            return queryset.filter(service_number__in=service_number_list)
        if self.value() == 'False':
            return queryset.exclude(service_number__in=service_number_list)


@admin.register(Selection)
class SelectionAdmin(admin.ModelAdmin):
    list_display = ['service_number','subscriber','uniqname','migrate','updated_by','update_date','processing_status','cut_date']
    ordering = ['-update_date']
    search_fields = ['service_number','uniqname','updated_by']
    list_filter = ['processing_status','migrate','cut_date',DuoListFilter,ZoomListFilter]
    form = SelectionForm



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


@admin.register(Ambassador)
class AmbassadorAdmin(admin.ModelAdmin):
    list_display = ['user','dept_group']
