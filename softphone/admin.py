from django.contrib import admin
from django import forms
from .models import Category, Selection, SelectionV, DuoUser, Ambassador
from django.urls import path
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib.contenttypes.models import ContentType
from .forms import migrate_choices
from django.contrib import messages
from project.utils import download_csv_from_queryset
from datetime import date


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


class SelectionBulkUpdateForm(forms.Form):
    processing_status = forms.ChoiceField(choices = processing_choices, required=False)
    cut_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=False)


class DefaultListFilter(admin.SimpleListFilter):

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'None':  # User selects 'None' vs no parameter selected.
                return queryset.filter(**{self.parameter_name + '__isnull': True}) 
            else:
                return queryset.filter(**{self.parameter_name: self.value()}) 

    def lookups(self, request, model_admin):
        return self.static_lookups


class ZoomListFilter(DefaultListFilter):
    title = 'Zoom Login'
    parameter_name = 'zoom_login'
    static_lookups = (('Y', 'Yes'), ('N', 'No'),)


class ProcessingStatusListFilter(DefaultListFilter):
    title = 'Processing Status'
    parameter_name = 'processing_status'
    static_lookups =  (('Selected', 'Selected'), ('Completed', 'Completed'),  ('On Hold', 'On Hold'),('Disconnected', 'Disconnected'), ('None', 'None'), )


class DuoListFilter(DefaultListFilter):
    title = 'Duo Phone'
    parameter_name = 'duo_phone'
    static_lookups =  (('Y', True), ('N', False))


class MigrateFilter(DefaultListFilter):
    title = 'Migrate'
    parameter_name = 'migrate'

    def lookups(self, request, model_admin):
        migrate_list = []
        for migrate in Selection.objects.distinct().order_by('migrate').values_list('migrate', flat=True):
            if migrate == None:
                migrate_list.append(('None',migrate))            
            else:
                migrate_list.append((migrate,migrate))

        return migrate_list


class CutDateListFilter(DefaultListFilter):
    title = 'Cut Date'
    parameter_name = 'cut_date'

    def lookups(self, request, model_admin):
        cut_date_list = []
        for cut_date in Selection.objects.distinct().order_by('cut_date').values_list('cut_date', flat=True):
            if cut_date == None:
                cut_date_list.append(('None',cut_date))            
            else:
                cut_date_list.append((cut_date,cut_date))

        return cut_date_list
    

@admin.register(SelectionV)
class SelectionAdmin(admin.ModelAdmin):
    show_full_result_count = False   # Removes one of the two count(*) queries
    list_display = ['service_number','dept_id','zoom_login','subscriber','uniqname','migrate','updated_by','update_date','processing_status','cut_date','building_code']
    ordering = ['-update_date']
    search_fields = ['service_number','uniqname','updated_by','building_code']
    list_filter = [ProcessingStatusListFilter
                   ,MigrateFilter
                   ,CutDateListFilter
                   ,DuoListFilter
                   ,ZoomListFilter]
    date_hierarchy = 'cut_date'   # Adds two queries
    form = SelectionForm
    actions = ['update_selections','download_csv']
    readonly_fields = ['zoom_login','duo_phone','dept_id','phone','subscriber_last_name','subscriber_first_name','subscriber_uniqname']

    def get_urls(self):
        urls = super().get_urls()

        download_url = [
            path('bulk_update/', self.bulk_update),
        ]
        return download_url + urls

    @admin.action(description='Download CSV')
    def download_csv(self, request, queryset):
        return download_csv_from_queryset(queryset, file_name='selections')

    @admin.action(description='Update selections')
    def update_selections(self, request, queryset):
        form = SelectionBulkUpdateForm()

        return TemplateResponse(
            request,
            'admin/softphone/selection/bulk_update.html',
            {'queryset': queryset,
            'opts': self.opts,
            'form': form
            }
        )

    def bulk_update(self, request):
        cut_date = request.POST.get('cut_date')

        if cut_date == '':
            cut_date = None

        sub_list = request.POST.getlist('subscriber')
        
        for sub in Selection.objects.filter(subscriber__in=sub_list):
            sub.cut_date = cut_date
            sub.processing_status = request.POST.get('processing_status')

            sub.save()
 
        return HttpResponseRedirect('/admin/softphone/selectionv/')


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
    list_display = ['dept_grp','uniqname']
    ordering = list_display
