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
from django.db.models import Q,F, Sum
from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required

from .models import Estimate, Material, Labor, Favorite, Item, Workorder, MaterialLocation, Project, ProjectView, EstimateView, UmOscNoteProfileV, NotificationManager, Notification, Technician
from .forms import FavoriteForm, EstimateForm, ProjectForm, MaterialForm, MaterialLocationForm, LaborForm


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

        else:  # open_workorder
            title = 'Search Open Preorders/Workorders'
            search_list = Workorder.objects.filter(status_name='Open').defer('status_name')

            for workorder in search_list:
                if workorder.building_number:
                    workorder.building = str(workorder.building_number) + ' - ' + workorder.building_name
                
                if len(workorder.comment_text) > 80:
                    workorder.comment = workorder.comment_text[0:80] + '...'
                else:
                    workorder.comment = workorder.comment_text

            template = 'bom/basic_search.html'

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
    item_list = Item.objects.get_active()

    return render(request, 'bom/item_lookup.html',
                    {'title': 'Item Lookup',
                    'item_list': item_list})

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