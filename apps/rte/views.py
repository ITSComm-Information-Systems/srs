from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from project.pinnmodels import UmRteLaborGroupV, UmRteTechnicianV, UmRteRateLevelV, UmRteCurrentTimeAssignedV, UmRteServiceOrderV, UmRteInput
from project.models import ActionLog
from django.http import JsonResponse
from datetime import datetime, timedelta, date
from django.db import connections
from django.db.models import Sum
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.functions import ExtractWeek

# Base RTE view
@permission_required('rte.add_umrteinput', raise_exception=True)
def load_rte(request):
    template = loader.get_template('rte/base_rte.html')

    context = {
        'title': 'Rapid Time Entry'
    }
    return HttpResponse(template.render(context, request))


def get_confirmation(request):
    template = loader.get_template('rte/submitted.html')

    context = {
        'title': 'Rapid Time Entry Submit',
    }

    return HttpResponse(template.render(context, request))

# Single technician, multiple orders
@permission_required('rte.add_umrteinput', raise_exception=True)
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

    if request.user.has_perm('rte.add_submitalltechs'):
        all_techs = UmRteTechnicianV.objects.all()
        tech_id = ''
        tech_name = ''
        assigned_groups = ''
    else:
        all_techs = UmRteTechnicianV.objects.filter(uniqname=request.user.username)
        tech_id = all_techs[0].labor_code
        tech_name = all_techs[0].labor_name_display2
        assigned_groups = list(UmRteLaborGroupV.objects.filter(wo_group_labor_code=tech_id).values('wo_group_name'))


    all_wos = UmRteServiceOrderV.objects.all()
    rate_levels = list(UmRteRateLevelV.objects.all().values('labor_rate_level_name'))

    context = {
        'wf': 'single',
        'all_techs': all_techs,
        'all_wos': all_wos,
        'tech_id': tech_id,
        'tech_name': tech_name,
        'assigned_groups': assigned_groups,
        'rate_levels': rate_levels,
        'title': 'Single Technician, Multiple Orders/Entries',
        'tab_list': tab_list,
        'num_tabs': len(tab_list),
    }

    return HttpResponse(template.render(context, request))

# Review single tech times
@permission_required('rte.add_umrteinput', raise_exception=True)
def single_submit(request):
    template = loader.get_template('rte/submitted.html')
    now = datetime.now()

    if request.method == 'POST':
        try:
            ActionLog.objects.create(user=request.user.username, url=request.path, data=request.POST, timestamp=now)
        except:
            print('error adding action single_submit')

        num_entries = request.POST.get('num_entries')
        tech_id = request.POST.get('tech_id')
        assigned_group = request.POST.get('assigned_group')

        for i in range(1, int(num_entries) + 1):
            work_order = request.POST.get(str(i) + '_work_order', 'Deleted')

            if work_order != 'Deleted':
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
                    date_added=now, # date.today(),
                    date_processed=None,
                    messages=None,
                    request_no=None)
                new_entry.save()

        # Add record to Pinnacle
        curr = connections['pinnacle'].cursor()
        uniqname = request.user.username
        try:
            curr.callproc('UM_RTE_INTERFACE_K.UM_MAINTAIN_WO_LABOR_P',[uniqname, now])
        except:
            print('error')
        curr.close()

    return HttpResponseRedirect('/apps/rte/confirmation/') 


# Log
@permission_required('rte.add_submitalltechs', raise_exception=True)
def get_action_log(request):
    template = loader.get_template('rte/actionlog.html')

    action_list = ActionLog.objects.all().order_by('-timestamp')

    context = {
        'title': 'RTE Action Log',
        'action_list': action_list,
    }

    return HttpResponse(template.render(context, request))

@permission_required('rte.add_submitalltechs', raise_exception=True)
def get_action_log_entry(request, id):
    template = loader.get_template('rte/actionlogentry.html')

    action = ActionLog.objects.get(id=id)

    entry_list = []
    for key, value in action.data.items():

        pos = key.find('_')
        if pos > 0:
            x = key[0:pos]
            if x.isnumeric():
                x = int(x) - 1
                if len(entry_list) < x+1:
                    entry_list.append({})
                entry_list[x][key[pos+1:]] = value

    start = action.timestamp - timedelta(milliseconds=800)
    input_list = UmRteInput.objects.filter(date_added__range=[start, action.timestamp])

    context = {
        'title': 'RTE Action Log Entry',
        'action': action,
        'entry_list': entry_list,
        'input_list': input_list,
    }

    return HttpResponse(template.render(context, request))


# Multiple technicians, single order
@permission_required('rte.add_submitalltechs', raise_exception=True)
def multiple_tech(request):
    template = loader.get_template('rte/workflow.html')

    tab_list = []

    # Select technician tab
    tab1 = {
        'name': 'tabSelect',
        'step': 'step1',
        'label': 'Select Work Order',
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

    context = {
        'wf': 'multiple',
        'title': 'Multiple Technicians, Single Work Order',
        'tab_list': tab_list,
        'num_tabs': len(tab_list),
        'all_wos': all_wos,
        'all_techs': all_techs,
        'rate_levels': rate_levels
    }

    return HttpResponse(template.render(context, request))


# Find assigned group based on tech ID
def get_assigned_group(request):
    techid = request.GET.get('techid', None)
    assigned_groups = list(UmRteLaborGroupV.objects.filter(wo_group_labor_code=techid).values())

    return JsonResponse(assigned_groups, safe=False)


# Submit multiple tech times
@permission_required('rte.add_submitalltechs', raise_exception=True)
def multiple_submit(request):
    template = loader.get_template('rte/submitted.html')
    now = datetime.now()

    if request.method == 'POST':
        try:
            ActionLog.objects.create(user=request.user.username, url=request.path, data=request.POST, timestamp=now)
        except:
            print('error adding action single_submit')

        num_entries = request.POST.get('num_entries')
        work_order = request.POST.get('work_order')

        for i in range(1, int(num_entries) + 1):
            tech_id = request.POST.get(str(i) + '_techid', 'Deleted')

            if tech_id != 'Deleted':
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
                    date_added=now, #date.today(),
                    date_processed=None,
                    messages=None,
                    request_no=None)
                new_entry.save()

        # Add record to Pinnacle
        curr = connections['pinnacle'].cursor()
        uniqname = request.user.username
        curr.callproc('UM_RTE_INTERFACE_K.UM_MAINTAIN_WO_LABOR_P',[uniqname, now])
        curr.close()

    return HttpResponseRedirect('/apps/rte/confirmation/') 


# Modify time
@permission_required('rte.add_umrteinput', raise_exception=True)
def update(request):
    template = loader.get_template('rte/workflow.html')

    tab_list = []

    # Select technician tab
    tab1 = {
        'name': 'techSelect',
        'step': 'step1',
        'label': 'Select a Technician',
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

    if request.user.has_perm('rte.add_submitalltechs'):
        all_techs = UmRteTechnicianV.objects.all()
    else:
        all_techs = UmRteTechnicianV.objects.filter(uniqname=request.user.username)
        
    all_wos = UmRteServiceOrderV.objects.all()

    context = {
        'wf': 'update',
        'title': 'Update Time',
        'tab_list': tab_list,
        'num_tabs': len(tab_list),
        'all_techs': all_techs,
        'all_wos': all_wos,
    }

    return HttpResponse(template.render(context, request))


def get_update_entries(request):
    techid = request.GET.get('techid', None)
    work_order = request.GET.get('work_order', None)
    date_start = request.GET.get('calendar_start', None)
    date_end = request.GET.get('calendar_end', None)
    date_range = request.GET.get('date_range', None)

    # Search by work order
    if work_order:
        results = UmRteCurrentTimeAssignedV.objects.select_related('rate_number').filter(status_name="Open",
                                                       billed="No",
                                                       labor_code=techid,
                                                       work_order_display=work_order).order_by('-assigned_date',
                                                                                           'work_order_display').values('work_order_display', 'assigned_date',
                                                                                           'actual_mins_display', 'rate_number__labor_rate_level_name', 'assn_wo_group_name',
                                                                                           'wo_labor_id')
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

        results = UmRteCurrentTimeAssignedV.objects.select_related('rate_number').filter(status_name="Open",
                                                       billed="No",
                                                       labor_code=techid,
                                                       assigned_date__gte=date_start,
                                                       assigned_date__lte=date_end).order_by('-assigned_date',
                                                                                           'work_order_display').values('work_order_display', 'assigned_date',
                                                                                           'actual_mins_display', 'rate_number__labor_rate_level_name', 'assn_wo_group_name',
                                                                                           'wo_labor_id')
        search_topic = 'Date Range'
        search_criteria = date_start.strftime('%b %d, %Y') + ' - ' + date_end.strftime('%b %d, %Y')

    rate_levels = [rate.labor_rate_level_name for rate in UmRteRateLevelV.objects.all()]
    assigned_groups = [group.wo_group_name for group in UmRteLaborGroupV.objects.filter(wo_group_labor_code=techid)]
    total_hours = format_time(results.aggregate(Sum('actual_mins'))['actual_mins__sum'] or 0)
    results = list(results)

    results.append({
        'rate_levels': rate_levels,
        'search_topic': search_topic,
        'search_criteria': search_criteria,
        'assigned_groups': assigned_groups,
        'total_hours': total_hours
        })

    return JsonResponse(results, safe=False)

# Submit updated times
@permission_required('rte.add_umrteinput', raise_exception=True)
def update_submit(request):
    now = datetime.now()
    template = loader.get_template('rte/submitted.html')

    if request.method == 'POST':
        try:
            ActionLog.objects.create(user=request.user.username, url=request.path, data=request.POST, timestamp=now)
        except:
            print('error adding action single_submit')

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
                date_added=now, #date.today(),
                date_processed=None,
                messages=None,
                request_no=None)
            new_entry.save()

        # Add record to Pinnacle
        curr = connections['pinnacle'].cursor()
        uniqname = request.user.username
        curr.callproc('UM_RTE_INTERFACE_K.UM_MAINTAIN_WO_LABOR_P',[uniqname, now])
        curr.close()

    return HttpResponseRedirect('/apps/rte/confirmation/') 


# Find open, unbilled entries based on tech ID
@permission_required('rte.add_umrteinput', raise_exception=True)
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
@permission_required('rte.add_umrteinput', raise_exception=True)
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


@permission_required('rte.add_umrteinput', raise_exception=True)
def view_time_display(request):
    template = loader.get_template('rte/view/display.html')

    techid = request.POST.get('techSearch')
    work_order = request.POST.get('workOrderSearch')
    date_start = request.POST.get('calendarRangeStart')
    date_end = request.POST.get('calendarRangeEnd')
    date_range = request.POST.get('dateRangeSelect')
    multi_week_view = False
    multi_weekly_results = None
    total_hours = 0
    if request.POST.get('viewLastButton'):
        date_range = request.POST.get('viewLastButton')

    # Search by work order
    if work_order:
        results = UmRteCurrentTimeAssignedV.objects.filter(labor_code=techid, work_order_display=
            work_order).order_by('-assigned_date','work_order_display')
        search_topic = 'Work Order'
        search_criteria = work_order

    # Search dates
    else:
        # Search by date range
        if date_range:
            date_start, date_end = get_date_range(date_range)
            if date_range == 'Last Month':
                multi_week_view = True
        else:
            date_start = datetime.strptime(date_start, '%Y-%m-%d')
            date_end = datetime.strptime(date_end, '%Y-%m-%d')

        if date_range == 'Last Month':
            today = datetime.now().date()
            date_end = today + timedelta(days=(6 - today.weekday() + 1) % 7)
            date_start = date_end - timedelta(weeks=5)
            weeks = [date_start + timedelta(weeks=i) for i in range(5)]
            running_hours = 0
            
            multi_weekly_results = []
            for week_start in weeks:
                week_start = week_start - timedelta(days=1)
                week_end = week_start + timedelta(days=6)
                week_data = UmRteCurrentTimeAssignedV.objects.filter(
                        labor_code=techid, 
                        assigned_date__gte=week_start,
                        assigned_date__lt=week_end
                    ).aggregate(
                        total=Sum('actual_mins')  # Calculate the sum of the data for the week
                    )
                total_hours_weekly = week_data['total'] if week_data['total'] else 0
                running_hours += total_hours_weekly
                multi_weekly_results.append({
                    'week_start': week_start,
                    'week_end': week_end,
                    'total': format_time(total_hours_weekly)
                })
            results = UmRteCurrentTimeAssignedV.objects.filter(labor_code=techid, assigned_date__gte=date_start,
                                                            assigned_date__lte=date_end).order_by('-assigned_date','work_order_display')
            search_criteria = (date_start - timedelta(days=1)).strftime('%b %d, %Y') + ' - ' + (date_end - timedelta(days=2)).strftime('%b %d, %Y')
            total_hours = format_time(running_hours)
        else:
            results = UmRteCurrentTimeAssignedV.objects.filter(labor_code=techid, assigned_date__gte=date_start,
                                                            assigned_date__lte=date_end).order_by('-assigned_date','work_order_display')
            search_criteria = date_start.strftime('%b %d, %Y') + ' - ' + date_end.strftime('%b %d, %Y')
            total_hours = format_time(results.aggregate(Sum('actual_mins'))['actual_mins__sum'] or 0)
            
        search_topic = 'Date Range'
        


    context = {
        'title': 'View Time',
        'techid': techid,
        'search_topic': search_topic,
        'search_criteria': search_criteria,
        'entries': results,
        'total_hours': total_hours,
        'multi_week_view': multi_week_view,
        'multi_weekly_results': multi_weekly_results
    }
    return HttpResponse(template.render(context, request))


# Get begin and end date, given date range
def get_date_range(date_range):
    date_end = datetime.date(datetime.now())

    if date_range == 'Last Week':
        today = date.today()
        idx = (today.weekday() + 1) % 7 # MON = 0, SUN = 6 -> SUN = 0 .. SAT = 6
        date_start = today - timedelta(7+idx)
        date_end = today - timedelta(7+idx-6)

    elif date_range == 'Last Month':
        date_start = date_end - timedelta(days=27)

    elif date_range == 'Last 6 Months':
        date_start = date_end - timedelta(days=183)

    else:
        print('unknown date range', date_range)
        date_start = None

    return date_start, date_end


# Splits duration into hours and minutes
def split_duration(duration):
    duration = duration.split(':')
    return int(duration[0]), int(duration[1])


def format_time(total_hours):
    hours, mins = divmod(total_hours, 60)
    if hours < 10:
        hours = '0' + str(hours)
    if mins < 10:
        mins = '0' + str(mins)
    total_hours = str(hours) + ':' + str(mins)
    return total_hours
