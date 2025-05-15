from django.http import HttpResponse, HttpResponseRedirect, JsonResponse 
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.forms import modelform_factory, modelformset_factory, inlineformset_factory
from project.pinnmodels import UmOscPreorderApiV,UmRteTechnicianV, UmRteLaborGroupV
from django.db.models import Q,F, Sum, IntegerField
from datetime import datetime
from django.db.models.functions import Cast, Substr
from django.contrib.auth.decorators import login_required, permission_required

from .models import *
from .forms import FavoriteForm, EstimateForm, ProjectForm, MaterialForm, MaterialLocationForm, LaborForm

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    Paragraph, FrameBreak, Flowable,
    Frame, PageTemplate, BaseDocTemplate,
    KeepInFrame, Spacer)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os

class WorkorderListView(ListView):
    #filterset_class = None
    template_name = 'bom/search.html'
    model = Estimate
    paginate_by = 100  # if pagination is desired

    field_types = {'date': ['is before', 'is after'],
                   'text': ['starts with', 'contains', 'is equal to'],
                   'number': ['greater than', 'equal to', 'less than'],
                   }

    field_list = [{'name': 'pre_order_number', 'type': 'number', 'label': 'Pre Order Number'},
                  {'name': 'work_order_prefix', 'type': 'text',
                      'label': 'Workorder Prefix'},
                  {'name': 'descr', 'type': 'number',
                      'label': 'Project Description'},
                  {'name': 'mgr', 'type': 'text', 'label': 'Project Manager'},
                  {'name': 'eng', 'type': 'text', 'label': 'Engineer'},
                  {'name': 'due_date', 'type': 'date', 'label': 'Due Date'}
                  ]

    def get_queryset(self):
        print('queryset', self.request.GET)

        queryset = Estimate.objects.order_by('-create_date')
        # queryset.filter(wo_type_code='PT')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.request.GET)
        filter_val = self.request.GET.get(
            'pre_order_number', 'give-default-value')
        for parm in self.request.GET:
            print(parm)
        print(filter_val)
        # Pass the filterset to the template - it provides the form.
        context['field_list'] = self.field_list
        context['field_types'] = self.field_types
        context['title'] = 'search'
        return context


class Search(PermissionRequiredMixin, View):
    permission_required = 'bom.can_access_bom'

    def get(self, request):
        search_list = Workorder.objects.all()

        filter = request.GET.get('filter', all)

        if filter == 'open_estimates':
            title = 'Open Estimates'
            search_list = EstimateView.objects.filter(status_name='Open')
            template = 'bom/search_estimates.html'
        elif filter == 'warehouse':
            title = 'Warehouse/Ordered'
            search_list = EstimateView.objects.filter(status__in=['Warehouse','Ordered']).order_by('-status','-pre_order_number')
            template = 'bom/search_warehouse.html'
        elif filter == 'quick':
            title = 'Search by Preorder'
            search_list = [] #EstimateView.objects.filter(status__in=['Warehouse','Ordered']).order_by('-status')
            template = 'bom/search_quick.html'
        elif filter == 'all_estimates':
            title = 'All Preorders/Workorder w/Estimates'
            search_list = EstimateView.objects.all()
            template = 'bom/search_estimates.html'
        elif filter == 'assigned_to_me':
            template = 'bom/search_estimates_networkengineering.html'
            title = 'Assigned to Me'
            search_list = EstimateView.objects.assigned_to(request.user.username)

            all_techs = UmRteTechnicianV.objects.filter(uniqname=request.user.username)
            if all_techs:
                tech_id = all_techs[0].labor_code
                assigned_groups = UmRteLaborGroupV.objects.filter(wo_group_labor_code=tech_id).values_list('wo_group_name',flat=True)

                if 'Network Operations' in assigned_groups:
                    template = 'bom/search_estimates_networkoperations.html'

                if 'Project Managers' in assigned_groups:
                    template = 'bom/search_estimates_projectmanagers.html'

        # else:  # open_workorder
        #     title = 'Search Open Preorders/Workorders'
        #     search_list = Workorder.objects.filter(status_name='Open').defer('status_name')

        #     for workorder in search_list:
        #         if workorder.building_number:
        #             workorder.building = str(workorder.building_number) + ' - ' + workorder.building_name
                
        #         if len(workorder.comment_text) > 80:
        #             workorder.comment = workorder.comment_text[0:80] + '...'
        #         else:
        #             workorder.comment = workorder.comment_text

        #     template = 'bom/basic_search.html'

        return render(request, template,
                      {'title': title,
                       'search_list': search_list,
                       })


@permission_required('bom.can_access_bom')
def search_ajax(request):

    q = request.GET.get('q', all)
    estimates = []

    for est in EstimateView.objects.filter(pre_order_number=q) | EstimateView.objects.filter(wo_number_display=q):
        text = f'{est.wo_number_display} ({est.pre_order_number})  Label:{est.label}'
        estimates.append({"id": est.id, "text": text})

    return JsonResponse({'results': estimates}, safe=False)

@permission_required('bom.can_access_bom')
def edit_project(request):
    estimate_id = request.POST['estimate_id']
    project_id = request.POST.get('project_id')
    woid = request.POST.get('woid')

    if project_id:
        project = Project.objects.get(id=project_id)
        engineer = project.netops_engineer
    else:
        project, created = Project.objects.get_or_create(woid=woid)
        project.woid = woid
        engineer = ''

    project.set_create_audit_fields(request.user.username)
    form = ProjectForm(request.POST, instance=project)
    if form.is_valid():
        project.save()
    
    if project.netops_engineer != engineer:
        project.notify_engineer(estimate_id)

    return HttpResponseRedirect(f'/apps/bom/estimate/{estimate_id}')


@permission_required('bom.can_access_bom')
def project_list(request):
    project_list = Project.objects.all()

    return render(request, 'bom/search_projects.html',
                    {'title': 'UMNET Project List',
                    'project_list': project_list})


@permission_required('bom.can_access_bom')
def item_lookup(request):

    return render(request, 'bom/item_lookup.html',
                    {'title': 'Item Lookup'})

@permission_required('bom.can_access_bom')
def item_lookup_endpoint(request):
    search_query = request.POST.get('item_code', '').strip().lower()
    item_list = Item.objects.get_active()


    if search_query:
        item_list = item_list.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(manufacturer__icontains=search_query) |
            Q(manufacturer_part_number__icontains=search_query)
        )

    return render(request, 'bom/partials/item_table_rows.html', {'item_list': item_list})

@permission_required('bom.can_access_bom')
def item_usage_count(request, item_pk):
    # Get the item object for the given pk
    item = get_object_or_404(Item, pk=item_pk)
    total_quantity = Material.objects.filter(item=item, material_location__estimate__status__in=[Estimate.WAREHOUSE, Estimate.ORDERED]).aggregate(Sum('quantity'))['quantity__sum']
    if total_quantity is None:
        total_quantity = 0

    return HttpResponse(str(total_quantity))

@permission_required('bom.can_access_bom')
def item_details(request, item_pk):
    # Get the item object for the given pk
    item = get_object_or_404(Item, pk=item_pk)
    total_quantity = Material.objects.filter(item=item, material_location__estimate__status__in=[Estimate.WAREHOUSE, Estimate.ORDERED]).aggregate(Sum('quantity'))['quantity__sum']
    return render(request, 'bom/item_details.html',{'total_quantity': total_quantity,'item': item,})

@permission_required('bom.can_access_bom')
def edit_material_location(request):

    material_location_id = request.POST['material_location_id']

    name = request.POST.get('material_location')
    descr = request.POST.get('material_location_description')

    mat = MaterialLocation.objects.get(id=material_location_id)

    if name:
        mat.name = name
    
    if descr:
        mat.description = descr
    else:
        mat.description = ''

    mat.save()

    return HttpResponseRedirect(f'/apps/bom/estimate/{mat.estimate_id}?tab=location')


@permission_required('bom.can_access_bom')
def add_new_part(request):

    estimate_id = request.POST['estimate_id']

    if request.POST['new_id'] == '0':
        mat = Material()
    else:
        mat = Material.objects.get(id=request.POST['new_id'])

    mat.set_create_audit_fields(request.user.username)
    location = request.POST.get('item_location')
    new_location = MaterialLocation.objects.get_or_create(estimate_id=estimate_id, name=location)
    mat.material_location = new_location[0]
    mat.price = request.POST.get('item_price')
    mat.quantity = request.POST.get('item_quantity')
    #mat.item_code = 'New'
    mat.item_description = request.POST.get('item_description')
    mat.manufacturer = request.POST.get('item_manufacturer')
    mat.manufacturer_part_number = request.POST.get('item_manufacturer_part_number')
    mat.save()

    return HttpResponseRedirect(f'/apps/bom/estimate/{estimate_id}')

@permission_required('bom.can_access_bom')
def add_pinnacle_note(request):

    estimate_id = request.POST['note_estimate_id']
    woid = request.POST['note_woid']
    subject = request.POST['note_subject']
    body = request.POST['note_body']

    if subject == 'Route to Project Manager':
        estimate = Estimate.objects.get(id=estimate_id)
        estimate.get_workorder()
        addr = f'{estimate.workorder.add_info_list_value_code_2}@umich.edu'
        print(f'notify PM: {addr}')
        NotificationManager().send_email(Notification.ROUTE_PM, estimate, [addr])

    note = UmOscNoteProfileV()
    note.note_type_code = 'Work Order'
    note.note_types_code = 'NOTE'
    note.note_subject = subject
    note.note_body = body
    note.note_author = request.user.username
    note.note_keyid_value = woid
    note.save()

    return HttpResponseRedirect(f'/apps/bom/estimate/{estimate_id}')

@permission_required('bom.can_access_bom')
def notify_warehouse(request):

    estimate_id = request.POST['estimate_id']
    estimate = Estimate.objects.get(id=estimate_id)
    estimate.notify_warehouse()

    note = UmOscNoteProfileV()
    note.note_type_code = 'Work Order'
    note.note_types_code = 'NOTE'
    note.note_subject = 'Notify Warehouse'
    note.note_body = 'Notify Warehouse'
    note.note_author = request.user.username
    note.note_keyid_value = estimate.woid
    note.save()

    return HttpResponseRedirect(f'/apps/bom/estimate/{estimate_id}')


@permission_required('bom.can_access_bom')
def create_estimate(request):

    estimate = Estimate()
    estimate.set_create_audit_fields(request.user.username)
    estimate.label = request.POST.get('estimate_label', 'new label')
    estimate.woid = request.POST['pre_order_id']
    estimate.save()

    return HttpResponseRedirect(f'/apps/bom/estimate/{estimate.id}')


@permission_required('bom.can_access_bom')
def upload_csv(request):

    estimate = Estimate.objects.get(id=request.POST['estimate_id'])
    result = estimate.import_material_from_csv(request.FILES['file'], request.user)

    return render(request, 'bom/import_log.html',
                    {'title': 'Import CSV',
                    'result': result,
                    'estimate': estimate})


class Estimates(PermissionRequiredMixin, View):
    permission_required = 'bom.can_access_bom'
    MaterialFormSet = modelformset_factory(Material,  fields=('quantity',) #,'vendor','release_number','staged','estimated_receive_date','order_date')
        , can_delete=True)
    LaborFormSet = inlineformset_factory(Estimate, Labor,  fields=(
        'group', 'description', 'hours', 'rate_type'), can_delete=True)


    def post(self, request, estimate_id):
        estimate = Estimate.objects.get(id=estimate_id)
        current_tab = request.POST.get('current_tab', '')

        material_formset = self.MaterialFormSet(
            request.POST, queryset=estimate.get_material(), prefix='material')

        form = EstimateForm(request.POST, instance=estimate)

        labor_formset = self.LaborFormSet(
            request.POST, instance=estimate, prefix='labor')

        if form.is_valid() and material_formset.is_valid() and labor_formset.is_valid():

            if form.has_changed() or material_formset.has_changed() or labor_formset.has_changed():
                estimate.updated_by = request.user.username
                estimate.update_date = datetime.now()
                estimate.save()

            if material_formset.has_changed():
                material_formset.save()

            if labor_formset.has_changed():
                labor_formset.save()

            return HttpResponseRedirect(f'/apps/bom/estimate/{estimate_id}/?tab={current_tab}')
        else:
            element = 0
            if request.user.has_perm('bom.can_update_bom_ordered'):
                element = 1

            print('error')

            if not form.is_valid():
                print('form', form.errors, form.is_bound)
            if not material_formset.is_valid(): 
                print('material_formset', material_formset.errors)
            if not labor_formset.is_valid():
                print('labor_formset', labor_formset.errors)
            #print(f'form={form}  material={material_formset}  labor={labor_formset}')

            return render(request, 'bom/estimate.html',
                {#'title': title,
                'form': form,
                'element': element,
                #'project_form': project_form,
                'material_formset': material_formset,
                'labor_formset': labor_formset,
                #'workorder': estimate.workorder,
                'estimate': estimate})

    def get(self, request, estimate_id):
        estimate = get_object_or_404(Estimate, pk=estimate_id)
        estimate.get_detail()

        element = 0
        if request.user.has_perm('bom.can_update_bom_ordered'):
            element = 1

        if hasattr(estimate.workorder, 'wo_number_display'):
            title = estimate.workorder.wo_number_display
        else:
            title = 'N/A'

        if estimate.project:
            project_form = ProjectForm(instance=estimate.project)
        else:
            project_form = ProjectForm()

        LaborFormSet = inlineformset_factory(
            Estimate, Labor, form=LaborForm, exclude=('user',), can_delete=True, can_order=True)
        labor_formset = LaborFormSet(instance=estimate, prefix='labor')

        MaterialFormSet = modelformset_factory(
            Material, form=MaterialLocationForm, exclude=('id',), extra=0)
        material_formset = MaterialFormSet(
            queryset=estimate.material_list, prefix='material')
        form = EstimateForm(instance=estimate)

        return render(request, 'bom/estimate.html',
                      {'title': title,
                       'form': form,
                       'element': element,
                       'project_form': project_form,
                       'material_formset': material_formset,
                       'labor_formset': labor_formset,
                       'workorder': estimate.workorder,
                       'estimate': estimate,})


class AddItem(PermissionRequiredMixin, View):
    permission_required = 'bom.can_access_bom'

    def post(self, request, estimate_id):
        #estimate_id = intrequest.POST['estimate_id']

        mat = Material()
        mat.set_create_audit_fields(request.user.username)
        mat.item_code = request.POST['item_code']
        mat.quantity = request.POST['item_quantity']
        new_location = MaterialLocation.objects.get_or_create(estimate_id=estimate_id, name=request.POST['item_location'])
        mat.material_location = new_location[0]
        mat.save()

        return HttpResponseRedirect(f'/apps/bom/estimate/{estimate_id}')

    def get(self, request, estimate_id):

        form = MaterialForm()
        item_list = Item.objects.get_active()
        location_list = MaterialLocation.objects.filter(estimate_id=estimate_id)

        return render(request, 'bom/add_item.html',
                      {'title': 'Add Existing Part',
                       'estimate_id': estimate_id,
                       'form': form,
                       'location_list': location_list,
                       'item_list': item_list, })




class Warehouse(PermissionRequiredMixin, View):
    permission_required = 'bom.can_update_bom_ordered'
    MaterialFormSet = modelformset_factory(Material,  fields=('status','quantity','vendor','release_number','staged','estimated_receive_date','order_date','reel_number')
        , can_delete=True)
    WarehouseForm = modelform_factory(Estimate, fields=("label", "status"))

    def post(self, request, estimate_id):
        estimate = Estimate.objects.get(id=estimate_id)
        current_tab = request.POST.get('current_tab', '')

        material_formset = self.MaterialFormSet(
            request.POST, queryset=estimate.get_material(), prefix='material')

        form = self.WarehouseForm(request.POST, instance=estimate)

        if form.is_valid() and material_formset.is_valid():

            if form.has_changed() or material_formset.has_changed():
                estimate.updated_by = request.user.username
                estimate.update_date = datetime.now()
                estimate.save()

            if material_formset.has_changed():
                material_formset.save()

            return HttpResponseRedirect(f'/apps/bom/warehouse/{estimate_id}/')
        else:
            element = 0
            if request.user.has_perm('bom.can_update_bom_ordered'):
                element = 1

            print('error')

            if not form.is_valid():
                print('form', form.errors, form.is_bound)
            if not material_formset.is_valid(): 
                print('material_formset', material_formset.errors)
            #print(f'form={form}  material={material_formset}  labor={labor_formset}')

            return render(request, 'bom/warehouse.html',
                {#'title': title,
                'form': form,
                'element': element,
                #'project_form': project_form,
                'material_formset': material_formset,
                #'workorder': estimate.workorder,
                'estimate': estimate})

    def get(self, request, estimate_id):
        estimate = get_object_or_404(Estimate, pk=estimate_id)
        estimate.get_detail()

        if hasattr(estimate.workorder, 'wo_number_display'):
            title = estimate.workorder.wo_number_display
        else:
            title = 'N/A'

        if estimate.project:
            project_form = ProjectForm(instance=estimate.project)
        else:
            project_form = ProjectForm()

        MaterialFormSet = modelformset_factory(
            Material, form=MaterialForm, exclude=('id',), extra=0)
        material_formset = MaterialFormSet(
            queryset=estimate.material_list.order_by('status','item_code'), prefix='material')
        form = self.WarehouseForm(instance=estimate)

        return render(request, 'bom/warehouse.html',
                      {'title': title,
                       'form': form,
                       #'element': element,
                       'project_form': project_form,
                       'material_formset': material_formset,
                       #'labor_formset': labor_formset,
                       'workorder': estimate.workorder,
                       'estimate': estimate})


class Favorites(PermissionRequiredMixin, View):
    permission_required = 'bom.can_access_bom'

    FavoriteFormSet = modelformset_factory(
        Favorite, exclude=('user',), can_delete=True, can_order=True)

    def post(self, request):

        formset = self.FavoriteFormSet(request.POST)

        instances = formset.save(commit=False)
        for instance in instances:
            instance.user_id = request.user.id

        formset.save()
        return HttpResponseRedirect('/apps/bom/favorites/')

    def get(self, request):
        formset = self.FavoriteFormSet(
            queryset=Favorite.objects.filter(user=request.user))
        item_list = Item.objects.get_active()

        return render(request, 'bom/favorites.html',
                      {'title': 'My Favorites',
                       'formset': formset,
                       'item_list': item_list, })


class NetOpsSearch(PermissionRequiredMixin, View):
    permission_required = 'bom.can_access_bom'

    def get(self, request):
        template = 'bom/netops.html'

        search_list = ProjectView.objects.filter(Q(status=2) | Q(status=3)).order_by('-woid')
        return render(request, template,
                      {'title': 'UMNet Projects',
                       'search_list': search_list})
    
class EngineeringSearch(PermissionRequiredMixin, View):
    permission_required = 'bom.can_access_bom'

    def get(self, request):
        template = 'bom/engineering_search.html'
        engineers = Technician.objects.filter(wo_group_code='Network Engineering').values_list('user_name', flat=True)

        for group in request.user.groups.all():
            print(group.name)
        search_list = EstimateView.objects.filter(
            Q(
                assigned_engineer__in=engineers,
                status='Estimate',
                engineer_status='NOT_COMPLETE',
                status_name='Open') |
            Q(
                status_name='Open',
                status__in=('Approved', 'Ordered', 'Warehouse'),
                engineer_status = 'NOT_COMPLETE',
                assigned_engineer__in=engineers)
            ).order_by(F('estimated_completion_date').desc(nulls_last=True))
        return render(request, template,
                    {'title': 'Engineering Projects',
                    'search_list': search_list})
   
@permission_required('bom.can_access_bom')
def estimate_search(request):
    template = 'bom/estimate_search.html'
    return render(request, template, {'title': 'All Preorders/Workorder w/Estimates'})

def estimate_search_endpoint(request):
    # Get the search query and selected statuses
    search_query = request.POST.get('search', '').strip()
    selected_statuses = request.POST.getlist('status')  # Get the list of selected checkboxes

    # Build the queryset based on the search query and selected statuses
    search_list = EstimateView.objects.exclude(estimated_start_date__isnull=True)

    if search_query:
        search_list = search_list.filter(
            Q(wo_number_display__icontains=search_query) |
            Q(pre_order_number__icontains=search_query) |
            Q(project_display__icontains=search_query) |
            Q(label__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(project_manager__icontains=search_query) |
            Q(assigned_engineer__icontains=search_query) |
            Q(assigned_netops__icontains=search_query) |
            Q(estimated_start_date__icontains=search_query) |
            Q(estimated_completion_date__icontains=search_query)
        )

    if selected_statuses:
        search_list = search_list.filter(status__in=selected_statuses)

    # Limit the results to the most recent 50 based on estimated_start_date
    search_list = search_list.order_by('-estimated_start_date')[:50]

    # If fewer than 50 results, pad with entries that have no estimated_start_date
    if len(search_list) < 50:
        padding_needed = 50 - len(search_list)
        padding_results = EstimateView.objects.filter(estimated_start_date__isnull=True)
        if search_query:
            padding_results = padding_results.filter(
                Q(wo_number_display__icontains=search_query) |
                Q(pre_order_number__icontains=search_query) |
                Q(project_display__icontains=search_query) |
                Q(label__icontains=search_query) |
                Q(status__icontains=search_query) |
                Q(project_manager__icontains=search_query) |
                Q(assigned_engineer__icontains=search_query) |
                Q(assigned_netops__icontains=search_query) |
                Q(estimated_completion_date__icontains=search_query)
            )
        if selected_statuses:
            padding_results = padding_results.filter(status__in=selected_statuses)

        # Add padding results to the search list
        search_list = list(search_list) + list(padding_results[:padding_needed])

    # Render the partial template with the filtered results
    search_list_size = len(search_list)
    if search_list_size == 0:
        template = 'bom/partials/no_results.html'
    else:
        template = 'bom/partials/estimate_search_table.html'
    return render(request, template, {'search_list': search_list})

@permission_required('bom.can_access_bom')
def open_preorder_search(request):
    template = 'bom/open_preorder_search.html'

    return render(request, template,
                {'title': 'Search Open Preorders/Workorders',
                })
@permission_required('bom.can_access_bom')
def search_mockup(request):
    template = 'bom/search_mockup.html'

    return render(request, template,
                {'title': 'Search Mockup',
                })

@permission_required('bom.can_access_bom')
def open_preorder_endpoint(request):
    if request.method == 'POST':
        search_query = request.POST.get('search', '')
        search_list = Workorder.objects.filter(
            Q(status_name='Open') & (
                Q(wo_number_display__icontains=search_query) |
                Q(pre_order_number__icontains=search_query) |
                Q(status_name__icontains=search_query) |
                Q(project_display__icontains=search_query) |
                Q(building_number__icontains=search_query) |
                Q(building_name__icontains=search_query) |
                Q(comment_text__icontains=search_query) 
            )
        ).defer('status_name')

        for workorder in search_list:
                if workorder.building_number:
                    workorder.building = str(workorder.building_number) + ' - ' + workorder.building_name
                
                if len(workorder.comment_text) > 80:
                    workorder.comment = workorder.comment_text[0:80] + '...'
                else:
                    workorder.comment = workorder.comment_text


    search_list_size = len(search_list)
    if search_list_size == 0:
        template = 'bom/partials/no_results.html'
    else:
        template = 'bom/partials/open_preorder_table.html'
    return render(request, template,
                {'search_list': search_list})

@permission_required('bom.can_access_bom')
def item_barcodes(request):
    if "selected_items" in request.session:
        del request.session["selected_items"]
    template = 'bom/item_barcodes.html'

    return render(request, template,
                {   'title': 'Item Barcodes',})

@permission_required('bom.can_access_bom')
def item_barcodes_endpoint(request):
    template = 'bom/partials/item_barcodes_rows.html'
    search_query = request.POST.get('item_code', '').strip().lower()

    item_list = ItemBarcode.objects.all()
    if search_query:
        item_list = item_list.filter(
            Q(commodity_code__icontains=search_query) |
            Q(commodity_name__icontains=search_query) |
            Q(manufacturer_part_nbr__icontains=search_query) |
            Q(warehouse_code__icontains=search_query) |
            Q(warehouse_name__icontains=search_query) )

    item_list = item_list.order_by('commodity_code')[:1000]
    
    return render(request, template,
                {'item_list': item_list})

@permission_required('bom.can_access_bom')
def add_selected_barcode_item(request):
    # Initialize the session variable if it doesn't exist
    if "selected_items" not in request.session:
        request.session["selected_items"] = []

    if request.method == "POST":
        # Retrieve the selected items from the session
        selected_items = request.session["selected_items"]

        # Get the item details from the POST request
        commodity_code = request.POST.get("item_commodity_code")
        commodity_name = request.POST.get("item_commodity_name")
        manufacturer_part_nbr = request.POST.get("item_manufacturer_part_nbr")
        warehouse_code = request.POST.get("item_warehouse_code")
        warehouse_name = request.POST.get("item_warehouse_name")
        min_reorder_lvl = request.POST.get("item_min_reorder_lvl")

        # Create a dictionary for the new item
        new_item = {
            "commodity_code": commodity_code,
            "commodity_name": commodity_name,
            "manufacturer_part_nbr": manufacturer_part_nbr,
            "warehouse_code": warehouse_code,
            "warehouse_name": warehouse_name,
            "min_reorder_lvl": min_reorder_lvl,
        }

        # Add the new item to the list if it's not already selected
        if new_item not in selected_items:
            if len(selected_items) < 16:
                selected_items.append(new_item)

        #remove the item from the list if it is already selected
        else:
            selected_items.remove(new_item)

        # Save the updated list back to the session
        request.session["selected_items"] = selected_items

        #pass selected items to the template
        return render(request, 'bom/partials/item_barcodes_card.html',
                     {'selected_items': selected_items})
    
font_path = os.path.join(settings.BASE_DIR, 'project','static', 'code39azalearegular2.ttf')
pdfmetrics.registerFont(TTFont('Code39Azalea', font_path))
class RoundedLabel(Flowable):
    def __init__(self, item, bg_color=None):  # Add bg_color parameter with default None
        super().__init__()
        self.item = item
        self.bg_color = bg_color  # Store the background color
        self.width = 4 * inch  # Label width
        self.height = 1.15 * inch  # Label height
        self.radius = 8  # Rounded corner radius

    def draw(self):
        # Draw the rounded rectangle with background if bg_color is set
        if self.bg_color:
            self.canv.setFillColor(colors.yellow)  # Use yellow color
            self.canv.roundRect(0, 0, self.width, self.height, self.radius, stroke=1, fill=1)
        else:
            # Draw just the border if no background color
            self.canv.roundRect(0, 0, self.width, self.height, self.radius, stroke=1, fill=0)

        # Rest of your drawing code remains the same
        self.canv.setFont('Helvetica-Bold', 12)
        self.canv.setFillColor(colors.red)
        self.canv.drawString(10, self.height - 13, self.item['commodity_code'])

        # Draw the "Min. Lvl:" text in regular font
        self.canv.setFont('Helvetica', 9)
        self.canv.setFillColor(colors.black)
        self.canv.drawString(170, self.height - 13, "Min. Lvl:")

        # Draw the variable part in bold and larger font
        self.canv.setFont('Helvetica-Bold', 12)
        self.canv.drawString(225, self.height - 13, str(self.item['min_reorder_lvl']))

        # Center the commodity_name
        self.canv.setFont('Helvetica-Bold', 8)
        text_width = pdfmetrics.stringWidth(self.item['commodity_name'], 'Helvetica-Bold', 8)
        x_position = (self.width / 2) - (text_width / 2)
        self.canv.drawString(x_position, self.height - 33, self.item['commodity_name'])

        # Draw the manufacturer_part_nbr
        self.canv.setFont('Helvetica-Bold', 11)
        text_width = pdfmetrics.stringWidth(self.item['manufacturer_part_nbr'], 'Helvetica-Bold', 11)
        x_position = (self.width / 2) - (text_width / 2)
        self.canv.drawString(x_position, self.height - 48, self.item['manufacturer_part_nbr'])

        # Draw the barcode
        text_width = pdfmetrics.stringWidth(self.item['manufacturer_part_nbr'], 'Code39Azalea', 24)
        x_position = (self.width / 2) - (text_width / 2)
        self.canv.setFont('Code39Azalea', 24)
        self.canv.drawString(x_position, self.height -73, self.item['commodity_code'])

import json
@permission_required('bom.can_access_bom')
def create_barcode_pdf(request):
    if request.method == 'POST':
        selected_items = request.session["selected_items"]
        data = json.loads(request.body)
        yellow_items = data.get('yellow_items', [])
        yellow_items = [item[5:] for item in yellow_items]

        buffer = BytesIO()
        doc = BaseDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=0.0125 * inch,
            rightMargin=0.125 * inch,
            topMargin=0.125 * inch,
            bottomMargin=0.125 * inch
        )

        # Define frames for two columns
        col_width = (doc.width - 0.25 * inch) / 2  # Account for 0.25" gap between columns
        frame1 = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            col_width,
            doc.height,
            id='col1'
        )
        frame2 = Frame(
            doc.leftMargin + col_width + 0.125 * inch,  # Add gap between columns
            doc.bottomMargin,
            col_width,
            doc.height,
            id='col2'
        )

        two_col_template = PageTemplate(id='TwoCol', frames=[frame1, frame2])
        doc.addPageTemplates([two_col_template])

        story = []
        items_per_column = 8  # 8 items per column (16 total per page)

        # Add labels to the story
        for item in selected_items:
            # Check if current item should have yellow background
            bg_color = 'yellow' if item['commodity_code'] in yellow_items else None
            
            story.append(RoundedLabel(item, bg_color=bg_color))  # Pass bg_color to RoundedLabel
            story.append(Spacer(0, 0.1 * inch))  # Add spacing between labels

        doc.build(story)
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

    return HttpResponse("Invalid request method", status=405)