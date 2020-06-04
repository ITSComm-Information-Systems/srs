from django.http import HttpResponse
from django.template import loader
from project.pinnmodels import UmRteLaborGroupV, UmRteTechnicianV, UmRteRateLevelV, UmRteCurrentTimeAssignedV, UmRteServiceOrderV
from django.http import JsonResponse
from datetime import datetime, timedelta

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


    all_wos = UmRteServiceOrderV.objects.all()
    all_techs = UmRteTechnicianV.objects.all()
    rate_levels = list(UmRteRateLevelV.objects.all().values('labor_rate_level_name'))

    # Load after search
    if request.method == 'POST':

        selected_wo = request.POST.get('workOrderSearch')

        context = {
            'wf': 'multiple',
            'title': 'Multiple Technicians, Single Work Order',
            'tab_list': tab_list,
            'num_tabs': len(tab_list),
            'all_wos': all_wos,
            'all_techs': all_techs,
            'rate_levels': rate_levels,
            'selected_wo': selected_wo
        }

        return HttpResponse(template.render(context, request))

    # Original load
    else:
        context = {
            'wf': 'multiple',
            'title': 'Multiple Technicians, Single Work Order',
            'tab_list': tab_list,
            'num_tabs': len(tab_list),
            'all_wos': all_wos
        }
        return HttpResponse(template.render(context, request))


# Find assigned group based on tech ID
def get_assigned_group(request):
    techid = request.GET.get('techid', None)
    print(techid)
    assigned_groups = list(UmRteLaborGroupV.objects.filter(wo_group_labor_code=techid).values())

    return JsonResponse(assigned_groups, safe=False)


# Submit multiple tech times
def multiple_submit(request):
    template = loader.get_template('rte/submitted.html')

    entries = []
    if request.method == 'POST':
        num_entries = request.POST.get('num_entries')
        work_order = request.POST.get('work_order')

        for i in range(1, int(num_entries) + 1):
            entry = {
                'tech_id': request.POST.get(str(i) + '_techid'),
                'work_order': work_order,
                'rate_level': request.POST.get(str(i) + '_rate'),
                'assigned_group': request.POST.get(str(i) + '_assigned_group'),
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


# Modify time
def update(request):
    template = loader.get_template('rte/update/update.html')

    all_techs = UmRteTechnicianV.objects.all()

    context = {
        'title': 'Update Time',
        'all_techs': all_techs,  # change to tech ID
    }
    return HttpResponse(template.render(context, request))


# Find open, unbilled entries based on tech ID
def select_times(request):
    template = loader.get_template('rte/update/select_times.html')

    techid = ''
    tech_name = ''
    if request.method == 'POST':
        tech = request.POST.get('techSearch')
        techid = tech.split(':')[0]
        tech_name = tech.split(':')[1]

    results = UmRteCurrentTimeAssignedV.objects.filter(status_name="Open",
                                                       billed="No",
                                                       labor_code=techid.upper()).order_by('assigned_date',
                                                                                           'work_order_display')

    context = {
        'title': 'Update Time',
        'techid': techid,
        'tech_name': tech_name,
        'entries': results
    }
    return HttpResponse(template.render(context, request))


# View times
def view_time_load(request):
    template = loader.get_template('rte/view/search.html')

    all_techs = UmRteTechnicianV.objects.all()
    all_wos = UmRteServiceOrderV.objects.all()

    context = {
        'title': 'View Time',
        'all_techs': all_techs,
        'all_wos': all_wos
    }
    return HttpResponse(template.render(context, request))


def view_time_display(request):
    template = loader.get_template('rte/view/display.html')

    techid = request.POST.get('techSearch')
    work_order = request.POST.get('workOrderSearch')
    date_start = request.POST.get('calendarRangeStart')
    date_end = request.POST.get('calendarRangeEnd')
    date_range = request.POST.get('dateRangeSelect')

    # Search by work order
    if work_order:
        results = UmRteCurrentTimeAssignedV.objects.filter(labor_code=techid, work_order_display=work_order).order_by('assigned_date','work_order_display')

    # Search dates
    else:
        # Search by date range
        if date_range:
            date_start, date_end = get_date_range(date_range)

        results = UmRteCurrentTimeAssignedV.objects.filter(labor_code=techid, assigned_date__gt=date_start,
                                                           assigned_date__lt=date_end).order_by('assigned_date','work_order_display')

    context = {
        'title': 'View Time',
        'date_start': date_start,
        'date_end': date_end,
        'entries': results
    }
    return HttpResponse(template.render(context, request))


# Get begin and end date, given date range
def get_date_range(date_range):
    date_end = datetime.date(datetime.now())

    if date_range == 'Last Week':
        date_start = date_end - timedelta(days=7)

    if date_range == 'Last 3 Months':
        date_start = date_end - timedelta(days=92)

    if date_range == 'Last 6 Months':
        date_start = date_end - timedelta(days=183)

    return date_start, date_end