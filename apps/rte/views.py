from django.http import HttpResponse
from django.template import loader
from project.pinnmodels import UmRteLaborGroupV, UmRteTechnicianV, UmRteRateLevelV, UmRteCurrentTimeAssignedV, UmRteServiceOrderV

# Base RTE view
def load_rte(request):
    template = loader.get_template('rte/base_rte.html')

    context = {
        'title': 'Rapid Time Entry'
    }
    return HttpResponse(template.render(context, request))

# Single technician, multiple orders
def single_tech(request):
    template = loader.get_template('rte/workflow.html')

    tab_list = []

    # Select technician tab
    tab1 = {
        'name': 'tabSelect',
        'step': 'step1',
        'label': 'Select a Technician',
        'template': 'rte/single/single_tech.html'
    }
    tab_list.append(tab1)

    # Select technician tab
    tab2 = {
        'name': 'inputTime',
        'step': 'step2',
        'label': 'Input Time',
        'template': 'rte/single/input_time.html'
    }
    tab_list.append(tab2)

    # Select technician tab
    tab3 = {
        'name': 'reviewSubmit',
        'step': 'step3',
        'label': 'Review and Submit',
        'template': 'rte/single/review_submit.html'
    }
    tab_list.append(tab3)


    all_techs = UmRteTechnicianV.objects.all()

    all_wos = UmRteServiceOrderV.objects.all()

    # Load after search
    if request.method == 'POST':

        tech_id = request.POST.get('techSearch')

        tech_name = UmRteTechnicianV.objects.get(labor_code=tech_id)

        assigned_groups = list(UmRteLaborGroupV.objects.filter(wo_group_labor_code=tech_id).values('wo_group_name'))

        rate_levels = list(UmRteRateLevelV.objects.all().values('labor_rate_level_name'))

        context = {
            'wf': 'single',
            'all_techs': all_techs,
            'all_wos': all_wos,
            'tech_id': tech_id,
            'tech_name': tech_name,
            'assigned_groups': assigned_groups,
            'rate_levels': rate_levels,
            'title': 'Single Technician, Multiple Orders',
            'tab_list': tab_list,
            'num_tabs': len(tab_list)
        }

        return HttpResponse(template.render(context, request))

    # Original load
    else:
        context = {
            'wf': 'single',
            'all_techs': all_techs,
            'title': 'Single Technician, Multiple Orders',
            'tab_list': tab_list
        }
        return HttpResponse(template.render(context, request))

# Review single tech times
def single_submit(request):
    template = loader.get_template('rte/submitted.html')

    entries = []
    if request.method == 'POST':
        num_entries = request.POST.get('num_entries')
        tech_id = request.POST.get('tech_id')
        assigned_group = request.POST.get('assigned_group')

        for i in range(1, int(num_entries) + 1):
            entry = {
                'tech_id': tech_id,
                'work_order': request.POST.get(str(i) + '_work_order'),
                'rate_level': request.POST.get(str(i) + '_rate'),
                'assigned_group': assigned_group,
                'assigned_date': request.POST.get(str(i) + '_assigned_date'),
                'duration': request.POST.get(str(i) + '_duration'),
                'notes': request.POST.get(str(i) + '_notes')
            }
            entries.append(entry)

    context = {
        'title': 'Rapid Time Entry Submit',
        'entries': entries
    }

    return HttpResponse(template.render(context, request))


# Multiple technicians, single order
def multiple_tech(request):
    template = loader.get_template('rte/workflow.html')

    tab_list = []

    # Select technician tab
    tab1 = {
        'name': 'tabSelect',
        'step': 'step1',
        'label': 'Select Technicians',
        'template': 'rte/multiple/multiple_tech.html'
    }
    tab_list.append(tab1)

    # Select technician tab
    tab2 = {
        'name': 'inputTime',
        'step': 'step2',
        'label': 'Input Time',
        'template': 'rte/multiple/input_time.html'
    }
    tab_list.append(tab2)

    # Select technician tab
    tab3 = {
        'name': 'reviewSubmit',
        'step': 'step3',
        'label': 'Review and Submit',
        'template': 'rte/multiple/review_submit.html'
    }
    tab_list.append(tab3)

    context = {
        'wf': 'double',
        'title': 'Multiple Technicians, Single Work Order',
        'tab_list': tab_list,
        'num_tabs': len(tab_list)
    }

    return HttpResponse(template.render(context, request))


# View/modify time
def update(request):
    template = loader.get_template('rte/update/update.html')

    context = {
        'title': 'View/Update Time',
        'tech_id': request.user.username,  # change to tech ID
    }
    return HttpResponse(template.render(context, request))


# Find times based on date and tech ID
def view_times(request):
    template = loader.get_template('rte/update/view_times.html')

    start_date = 'N/A'
    end_date = 'N/A'
    techid = ''
    if request.method == 'POST':
        start_date = request.POST.get('date-start')
        end_date = request.POST.get('date-end')
        techid = request.POST.get('techid')

    results = UmRteCurrentTimeAssignedV.objects.filter(assigned_date__gte=start_date,
                                                       assigned_date__lte=end_date,
                                                       labor_code=techid.upper()).order_by('work_order_display',
                                                                                           'assigned_date')

    context = {
        'title': 'View/Update Time',
        'techid': techid,
        'start_date': start_date,
        'end_date': end_date,
        'entries': results
    }
    return HttpResponse(template.render(context, request))