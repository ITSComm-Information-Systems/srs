from django.http import HttpResponse
from django.template import loader
from project.pinnmodels import UmRteLaborGroupV, UmRteTechnicianV, UmRteRateLevelV, UmRteCurrentTimeAssignedV, UmRteServiceOrderV, UmRteInput
from django.http import JsonResponse
from datetime import datetime, timedelta, date
from django.db import connections
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

# Check if user has a tech ID
def has_techid(user):
    if UmRteTechnicianV.objects.filter(uniqname=user.username).exists():
        return True
    else:
        raise PermissionDenied

# Base RTE view
@user_passes_test(has_techid)
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

    if request.user.groups.filter(name="RTE Admin").exists():
        all_techs = UmRteTechnicianV.objects.all()
    else:
        all_techs = UmRteTechnicianV.objects.filter(uniqname=request.user.username)

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

    if request.method == 'POST':
        num_entries = request.POST.get('num_entries')
        tech_id = request.POST.get('tech_id')
        assigned_group = request.POST.get('assigned_group')

        for i in range(1, int(num_entries) + 1):
            work_order = request.POST.get(str(i) + '_work_order')
            rate_level = UmRteRateLevelV.objects.get(labor_rate_level_name=request.POST.get(str(i) + '_rate'))
            assigned_date = request.POST.get(str(i) + '_assigned_date')
            duration = request.POST.get(str(i) + '_duration')
            duration_hours, duration_mins = split_duration(duration)
            notes = request.POST.get(str(i) + '_notes')

            service_order = UmRteServiceOrderV.objects.get(full_prord_wo_number=request.POST.get(str(i) + '_work_order'))
            tech = UmRteTechnicianV.objects.get(labor_code=tech_id)
            assigned_group_q = UmRteLaborGroupV.objects.get(wo_group_name=assigned_group, wo_group_labor_code=tech_id)

            formatted_date = datetime.strptime(assigned_date, '%Y-%m-%d')

            new_entry = UmRteInput(
                uniqname=request.user.username,
                wo_labor_id=None,
                wo_tcom_id=service_order.wo_tcom_id,
                full_prord_wo_number=service_order.full_prord_wo_number,
                labor_id=tech.labor_id,
                labor_code=tech.labor_code,
                wo_group_labor_group_id=assigned_group_q.wo_group_labor_group_id,
                wo_group_code=assigned_group_q.wo_group_code,
                assigned_date=formatted_date.date(),
                complete_date=formatted_date.replace(hour=duration_hours, minute=duration_mins),
                rate_number=rate_level,
                actual_mins_display=duration,
                notes=notes,
                date_added=date.today(),
                date_processed=None,
                messages=None,
                request_no=None)
            new_entry.save()

        # Add record to Pinnacle
        curr = connections['pinnacle'].cursor()
        uniqname = request.user.username
        datetime_added = date.today()
        try:
            curr.callproc('UM_RTE_INTERFACE_K.UM_MAINTAIN_WO_LABOR_P',[uniqname, datetime_added])
        except:
            print('error')
        curr.close()

    context = {
        'title': 'Rapid Time Entry Submit'
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
        selected_wo_desc = all_wos.get(full_prord_wo_number=selected_wo).comment_text

        context = {
            'wf': 'multiple',
            'title': 'Multiple Technicians, Single Work Order',
            'tab_list': tab_list,
            'num_tabs': len(tab_list),
            'all_wos': all_wos,
            'all_techs': all_techs,
            'rate_levels': rate_levels,
            'selected_wo': selected_wo,
            'selected_wo_desc': selected_wo_desc
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
    assigned_groups = list(UmRteLaborGroupV.objects.filter(wo_group_labor_code=techid).values())

    return JsonResponse(assigned_groups, safe=False)


# Submit multiple tech times
def multiple_submit(request):
    template = loader.get_template('rte/submitted.html')

    if request.method == 'POST':
        num_entries = request.POST.get('num_entries')
        work_order = request.POST.get('work_order')

        for i in range(1, int(num_entries) + 1):
            tech_id = request.POST.get(str(i) + '_techid')
            assigned_group = request.POST.get(str(i) + '_assigned_group')
            rate_level = UmRteRateLevelV.objects.get(labor_rate_level_name=request.POST.get(str(i) + '_rate'))
            assigned_date = request.POST.get(str(i) + '_assigned_date')
            duration = request.POST.get(str(i) + '_duration')
            duration_hours, duration_mins = split_duration(duration)
            notes = request.POST.get(str(i) + '_notes')

            service_order = UmRteServiceOrderV.objects.get(full_prord_wo_number=work_order)
            tech = UmRteTechnicianV.objects.get(labor_code=tech_id)
            assigned_group = UmRteLaborGroupV.objects.get(wo_group_name=assigned_group, wo_group_labor_code=tech_id)

            formatted_date = datetime.strptime(assigned_date, '%Y-%m-%d')

            new_entry = UmRteInput(
                uniqname=request.user.username,
                wo_labor_id=None,
                wo_tcom_id=service_order.wo_tcom_id,
                full_prord_wo_number=service_order.full_prord_wo_number,
                labor_id=tech.labor_id,
                labor_code=tech.labor_code,
                wo_group_labor_group_id=assigned_group.wo_group_labor_group_id,
                wo_group_code=assigned_group.wo_group_code,
                assigned_date=formatted_date.date(),
                complete_date=formatted_date.replace(hour=duration_hours, minute=duration_mins),
                rate_number=rate_level,
                actual_mins_display=duration,
                notes=notes,
                date_added=date.today(),
                date_processed=None,
                messages=None,
                request_no=None)
            new_entry.save()

        # Add record to Pinnacle
        curr = connections['pinnacle'].cursor()
        uniqname = request.user.username
        datetime_added = date.today()
        curr.callproc('UM_RTE_INTERFACE_K.UM_MAINTAIN_WO_LABOR_P',[uniqname, datetime_added])
        curr.close()

    context = {
        'title': 'Rapid Time Entry Submit',
    }

    return HttpResponse(template.render(context, request))


# Modify time
def update(request):
    template = loader.get_template('rte/workflow.html')

    tab_list = []

    # Select technician tab
    tab1 = {
        'name': 'techSelect',
        'step': 'step1',
        'label': 'Select Technician',
        'template': 'rte/update/update.html'
    }
    tab_list.append(tab1)

    # Select entries to edit tab
    tab2 = {
        'name': 'selectEntries',
        'step': 'step2',
        'label': 'Select Entries',
        'template': 'rte/update/select_times.html'
    }
    tab_list.append(tab2)

    # Edit entries tab
    tab3 = {
        'name': 'editEntries',
        'step': 'step3',
        'label': 'Edit Entries',
        'template': 'rte/update/edit_times.html'
    }
    tab_list.append(tab3)

    # Review and Submit tab
    tab4 = {
        'name': 'reviewStep',
        'step': 'step4',
        'label': 'Review and Submit',
        'template': 'rte/update/review_submit.html'
    }
    tab_list.append(tab4)

    if request.user.groups.filter(name="RTE Admin").exists():
        all_techs = UmRteTechnicianV.objects.all()
    else:
        all_techs = UmRteTechnicianV.objects.filter(uniqname=request.user.username)
        
    rate_levels = [rate.labor_rate_level_name for rate in UmRteRateLevelV.objects.all()]

    # Load after search
    if request.method == 'POST':
        selected_tech = request.POST.get('techSearch')
        results = UmRteCurrentTimeAssignedV.objects.filter(status_name="Open",
                                                       billed="No",
                                                       labor_code=selected_tech).order_by('assigned_date',
                                                                                           'work_order_display')
        assigned_groups = [group.wo_group_name for group in UmRteLaborGroupV.objects.filter(wo_group_labor_code=selected_tech)]

        context = {
            'wf': 'update',
            'title': 'Update Time',
            'tab_list': tab_list,
            'num_tabs': len(tab_list),
            'all_techs': all_techs,
            'rate_levels': rate_levels,
            'assigned_groups': assigned_groups,
            'techid': selected_tech,
            'entries': results
        }

        return HttpResponse(template.render(context, request))

    # Original load
    else:
        context = {
            'wf': 'update',
            'title': 'Update Time',
            'tab_list': tab_list,
            'num_tabs': len(tab_list),
            'all_techs': all_techs
        }
        return HttpResponse(template.render(context, request))

# Submit updated times
def update_submit(request):
    template = loader.get_template('rte/submitted.html')

    if request.method == 'POST':
        num_entries = request.POST.get('num_entries')
        tech_id = request.POST.get('tech_id')

        for i in range(1, int(num_entries) + 1):
            work_order = request.POST.get(str(i) + '_work_order')
            rate_level = UmRteRateLevelV.objects.get(labor_rate_level_name=request.POST.get(str(i) + '_rate'))
            assigned_date = request.POST.get(str(i) + '_assigned_date')
            duration = request.POST.get(str(i) + '_duration')
            duration_hours, duration_mins = split_duration(duration)
            assigned_group = request.POST.get(str(i) + '_assigned_group')
            notes = request.POST.get(str(i) + '_notes')
            wo_labor_id = request.POST.get(str(i) + '_wo_labor_id')

            service_order = UmRteServiceOrderV.objects.get(full_prord_wo_number=request.POST.get(str(i) + '_work_order'))
            tech = UmRteTechnicianV.objects.get(labor_code=tech_id)
            assigned_group = UmRteLaborGroupV.objects.get(wo_group_name=assigned_group, wo_group_labor_code=tech_id)

            formatted_date = datetime.strptime(assigned_date, '%Y-%m-%d')

            print(formatted_date.replace(hour=duration_hours, minute=duration_mins))

            new_entry = UmRteInput(
                uniqname=request.user.username,
                wo_labor_id=wo_labor_id,
                wo_tcom_id=service_order.wo_tcom_id,
                full_prord_wo_number=service_order.full_prord_wo_number,
                labor_id=tech.labor_id,
                labor_code=tech.labor_code,
                wo_group_labor_group_id=assigned_group.wo_group_labor_group_id,
                wo_group_code=assigned_group.wo_group_code,
                assigned_date=formatted_date.date(),
                complete_date=formatted_date.replace(hour=duration_hours, minute=duration_mins),
                rate_number=rate_level,
                actual_mins_display=duration,
                notes=notes,
                date_added=date.today(),
                date_processed=None,
                messages=None,
                request_no=None)
            new_entry.save()

        # Add record to Pinnacle
        curr = connections['pinnacle'].cursor()
        uniqname = request.user.username
        datetime_added = date.today()
        curr.callproc('UM_RTE_INTERFACE_K.UM_MAINTAIN_WO_LABOR_P',[uniqname, datetime_added])
        curr.close()

    context = {
        'title': 'Rapid Time Entry Submit',
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
        search_topic = 'Work Order'
        search_criteria = work_order

    # Search dates
    else:
        # Search by date range
        if date_range:
            date_start, date_end = get_date_range(date_range)
        else:
            date_start = datetime.strptime(date_start, '%Y-%m-%d')
            date_end = datetime.strptime(date_end, '%Y-%m-%d')

        results = UmRteCurrentTimeAssignedV.objects.filter(labor_code=techid, assigned_date__gt=date_start,
                                                           assigned_date__lt=date_end).order_by('assigned_date','work_order_display')
        search_topic = 'Date Range'
        search_criteria = date_start.strftime('%b %d, %Y') + ' - ' + date_end.strftime('%b %d, %Y')

    context = {
        'title': 'View Time',
        'techid': techid,
        'search_topic': search_topic,
        'search_criteria': search_criteria,
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

# Splits duration into hours and minutes
def split_duration(duration):
    duration = duration.split(':')
    return int(duration[0]), int(duration[1])
