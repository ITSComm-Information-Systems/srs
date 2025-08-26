from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from project.pinnmodels import UmRteLaborGroupV, UmRteTechnicianV, UmRteRateLevelV, UmRteCurrentTimeAssignedV, UmRteServiceOrderV, UmRteInput, UmOscPreorderApiAbstract
from project.models import ActionLog
from django.http import JsonResponse
from datetime import datetime, timedelta, date
from django.db import connections
from django.db.models import Sum, Q
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.functions import ExtractWeek
from django.core import serializers
from ..bom.models import Workorder, Estimate, PreOrder, Labor, EstimateView
from collections import defaultdict
from django.views.decorators.cache import cache_page

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
        total_hours = format_time(results.aggregate(Sum('actual_mins'))['actual_mins__sum'] or 0)

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


GROUP_CONFIG = {
    # Submitted hours groups (UM_RTE_LABOR_GROUP_V - WO_GROUP_CODE)
    #This prefix is used to match the group codes in the input entries
    #e.g. network_ops_estimated_hours, osp_tech_estimated_hours etc
    'submitted_groups_prefix': {
        'Network Engineering': {'field': 'network'},
        'Drafting': {'field': 'drafting'},
        'Facilities Eng': {'field': 'facilities'},
        'Video Eng': {'field': 'video'},
        'Proj Mgr': {'field': 'project_manager'},
        'Network Operation': {'field': 'network_ops'},
        'OSP Tech': {'field': 'osp_tech'},
        'FSU': {'field': 'fsu'},
    },
    
    # Estimated hours groups (um_bom_labor_group_v - NAME)
    'estimated_groups': {
        'Network Eng': {'field': 'network', 'submitted_group': 'Network Engineering'},
        'Drafting': {'field': 'drafting', 'submitted_group': 'Drafting'},
        'Facilities Eng.': {'field': 'facilities', 'submitted_group': 'Facilities Eng'},
        'Video Eng': {'field': 'video', 'submitted_group': 'Video Eng'},
        'Project Mgt': {'field': 'project_manager', 'submitted_group': 'Proj Mgr'},
        'Network Ops': {'field': 'network_ops', 'submitted_group': 'Network Operation'},
        'FSU - OSP': {'field': 'osp_tech', 'submitted_group': 'OSP Tech'},
        'FSU - ISP': {'field': 'fsu', 'submitted_group':'FSU'}  # Not used in submitted hours
    }
}

def initialize_group_data():
    """Initialize all data structures for group calculations"""
    return {
        'group_uniqname_hours': {},
        'total_group_hours': {},
        'group_submitted_hours': {group: 0.00 for group in GROUP_CONFIG['submitted_groups_prefix']},
        'group_hover_strings': {group: '' for group in GROUP_CONFIG['submitted_groups_prefix']},
        'group_cell_classes': {group: '' for group in GROUP_CONFIG['submitted_groups_prefix']},
        'group_estimated_hours': {group: 0.00 for group in GROUP_CONFIG['estimated_groups']}
    }

def process_input_entries(input_entries, data):
    """Process input entries to calculate submitted hours"""
    for input_entry in input_entries:
        if input_entry.assn_wo_group_code in data['group_submitted_hours']:
            uniqname = input_entry.labor_code
            group = input_entry.assn_wo_group_code
            
            # Convert HH:MM to hours
            hh, mm = map(int, input_entry.actual_mins_display.split(':'))
            hours = hh + mm / 60
            
            # Update submitted hours
            data['group_submitted_hours'][group] += hours
            
            # Update uniqname hours tracking
            if group not in data['group_uniqname_hours']:
                data['group_uniqname_hours'][group] = {}
            data['group_uniqname_hours'][group].setdefault(uniqname, 0)
            data['group_uniqname_hours'][group][uniqname] += hours
            
            # Update total group hours
            data['total_group_hours'].setdefault(group, 0)
            data['total_group_hours'][group] += hours

def process_labor_entries(labor, data):
    """Process labor entries to calculate estimated hours"""
    for l in labor:
        if l.group.name in data['group_estimated_hours']:
            data['group_estimated_hours'][l.group.name] += float(l.hours)

def generate_hover_strings(data):
    """Generate hover strings showing uniqname hours breakdown"""
    for group, uniqnames in data['group_uniqname_hours'].items():
        uniqname_strings = [f"{uniqname}: {total_hours}" for uniqname, total_hours in uniqnames.items()]
        data['group_hover_strings'][group] = " | ".join(uniqname_strings)

def calculate_cell_classes(data):
    """Determine CSS classes for cells based on hours comparison"""
    for group in data['group_submitted_hours']:
        submitted_hours = data['group_submitted_hours'][group]
        
        # Find matching estimated hours group
        estimated_group = next(
            (eg for eg, config in GROUP_CONFIG['estimated_groups'].items() 
             if config.get('submitted_group') == group),
            None
        )
        
        if estimated_group:
            estimated_hours = data['group_estimated_hours'][estimated_group]
            
            if estimated_hours == 0 and submitted_hours == 0:
                data['group_cell_classes'][group] = ''
            elif submitted_hours > estimated_hours:
                data['group_cell_classes'][group] = 'table-danger'
            elif submitted_hours > estimated_hours * 0.8:
                data['group_cell_classes'][group] = 'table-warning'
            else:
                data['group_cell_classes'][group] = 'table-success'

def calculate_hours_and_classes(input_entries, labor):
    """Calculate all hours and determine cell classes"""
    data = initialize_group_data()
    
    process_input_entries(input_entries, data)
    process_labor_entries(labor, data)
    generate_hover_strings(data)
    calculate_cell_classes(data)
    
    return data

def apply_hours_to_estimate(estimate, hours_and_classes):
    """Apply all calculated hours to the estimate object"""
    # Set basic fields
    estimate.group_uniqname_hours = hours_and_classes['group_uniqname_hours']
    estimate.total_group_hours = hours_and_classes['total_group_hours']
    
    # Set all group-specific fields using the config
    for group, config in GROUP_CONFIG['submitted_groups_prefix'].items():
        field_prefix = f"{config['field']}_group"
        
        # Submitted hours
        setattr(estimate, f"{field_prefix}_submitted_hours", 
                hours_and_classes['group_submitted_hours'].get(group, 0))
        
        # Hover strings
        setattr(estimate, f"{field_prefix}_hover_string", 
                hours_and_classes['group_hover_strings'].get(group, ''))
        
        # Cell classes
        setattr(estimate, f"{field_prefix}_cell_class", 
                hours_and_classes['group_cell_classes'].get(group, ''))
    
    # Set estimated hours
    for group, config in GROUP_CONFIG['estimated_groups'].items():
        if config['field']:  # Skip groups without a field mapping
            setattr(estimate, f"{config['field']}_group_estimated_hours", 
                    hours_and_classes['group_estimated_hours'].get(group, 0))

@permission_required('bom.can_access_bom')
@cache_page(60 * 2)
def actual_v_estimate(request):
    """Main view function for actual vs estimate comparison"""
    username = request.user.username
    url = request.path.strip('/').split('/')
    slug = url[-1]

    if slug == 'actual-vs-estimate-open':
        template_name = 'rte/view/actual-vs-estimate-open.html'
        estimates = list(EstimateView.objects.filter(
            Q(project_manager=username) | Q(assigned_engineer=username) | Q(assigned_netops=username)
        ).exclude(status__in=['Rejected', 'Cancelled', 'Completed']
        ).exclude(estimated_start_date__isnull=True
        ).order_by('-estimated_start_date')[:250])
    else:
        template_name = 'rte/view/actual-vs-estimate-completed.html'
        estimates = list(EstimateView.objects.filter(
            Q(project_manager=username) | Q(assigned_engineer=username) | Q(assigned_netops=username)
        ).filter(status__in=['Completed'])[:550])

    # Batch fetch related Labor and ServiceOrder objects
    estimate_ids = [e.id for e in estimates]
    pre_order_numbers = [e.pre_order_number for e in estimates]

    labor_map = defaultdict(list)
    for l in Labor.objects.filter(estimate_id__in=estimate_ids):
        labor_map[l.estimate_id].append(l)

    service_order_map = {so.pre_order_number: so for so in UmRteServiceOrderV.objects.filter(pre_order_number__in=pre_order_numbers)}

    # Batch fetch all relevant UmRteCurrentTimeAssignedV entries
    full_prord_wo_numbers = [service_order_map.get(e.pre_order_number).full_prord_wo_number
                                for e in estimates if e.pre_order_number in service_order_map]
    input_entries_map = defaultdict(list)
    for entry in UmRteCurrentTimeAssignedV.objects.filter(work_order_display__in=full_prord_wo_numbers):
        input_entries_map[entry.work_order_display].append(entry)

    # Process each estimate
    for estimate in estimates:
        labor = labor_map.get(estimate.id, [])
        service_order = service_order_map.get(estimate.pre_order_number)
        full_prord_wo_number = service_order.full_prord_wo_number if service_order else None
        input_entries = input_entries_map.get(full_prord_wo_number, []) if full_prord_wo_number else []

        hours_and_classes = calculate_hours_and_classes(input_entries, labor)
        apply_hours_to_estimate(estimate, hours_and_classes)

    template = loader.get_template(template_name)
    context = {
        'title': 'Actual vs Estimated Hours',
        'estimates': estimates
    }
    return HttpResponse(template.render(context, request))

@permission_required('bom.can_access_bom')
@cache_page(60 * 2)
def employee_time_report(request):
    # 1. Get all groups and their members (unique groups only)
    groups_qs = UmRteLaborGroupV.objects.all()
    seen = set()
    groups = []
    for g in groups_qs:
        if g.wo_group_name not in seen:
            groups.append(g)
            seen.add(g.wo_group_name)

    group_workers = defaultdict(list)
    for tech in UmRteTechnicianV.objects.all():
        for group in UmRteLaborGroupV.objects.filter(wo_group_labor_code=tech.labor_code):
            group_workers[group.wo_group_name].append(tech)

    # 2. Define week range (e.g., last 6 weeks)
    today = datetime.today().date()
    number_of_weeks_to_display = 5
    week_starts = [(today - timedelta(days=today.weekday())) - timedelta(weeks=i) for i in range(number_of_weeks_to_display)][::-1]

    # 3. Gather hours per worker per week
    worker_hours = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    # Structure: worker_hours[group][worker][week_start] = hours

    # Query all relevant time entries in one go
    min_date = week_starts[0]
    max_date = week_starts[-1] + timedelta(days=6)
    entries = UmRteCurrentTimeAssignedV.objects.filter(
        assigned_date__gte=min_date,
        assigned_date__lte=max_date
    )

    for entry in entries:
        group = entry.assn_wo_group_name
        worker = entry.labor_code
        # Find the week start for this entry
        week_start = entry.assigned_date - timedelta(days=entry.assigned_date.weekday())
        # Convert HH:MM to float hours
        hh, mm = map(int, entry.actual_mins_display.split(':'))
        hours = hh + mm / 60
        worker_hours[group][worker][week_start] += hours

    # 4. Prepare context for template
    context = {
        'groups': groups,
        'group_workers': group_workers,
        'week_starts': week_starts,
        'worker_hours': worker_hours,
        'title': 'Weekly Worker Hours by Group',
    }
    template = loader.get_template('rte/view/employee-time-report.html')
    return HttpResponse(template.render(context, request))