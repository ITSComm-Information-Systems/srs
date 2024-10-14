from django.shortcuts import render
from datetime import datetime
from project.pinnmodels import UmOscServiceProfileV
from oscauth.models import AuthUserDept
from django.contrib.auth.decorators import permission_required


@permission_required('oscauth.can_report', raise_exception=True)
def get_usage_report(request):
    context = {'title': 'Total Usage by Month'}
    phone_number = request.GET.get('phone_number')

    if phone_number:
        phone_number = phone_number.replace('-','').replace('(','').replace(')','').replace(' ', '')
        locations = UmOscServiceProfileV.objects.filter(service_number=phone_number).order_by('-start_date').values()

        if not locations:
            context['message'] = f'Phone Number not found: {phone_number}'
        else:
            phone_dept = locations[0]['deptid']
            if phone_dept in AuthUserDept.get_order_departments(request.user).values_list('dept', flat=True):
                subscriber_id = locations[0]['subscriber_id']
                context['phone_number'] = phone_number
                context = {**context, **get_usage_totals(subscriber_id)}
            else:
                context['message'] = f'You are not authorized for dept: {phone_dept}'

    return render(request, 'oscauth/usage.html', context)


def get_usage_totals(subscriber_id):

    from project.utils import get_query_result

    current_month = datetime.now().month
    current_year = datetime.now().year

    headings = ['Call Type']
    pivot_list = '('

    for i in range(1,7):

        mon = datetime(current_year, current_month, 1)
        pivot_list = pivot_list + "'" + mon.strftime('%Y-%m') + "',"
        headings.append(mon.strftime('%B %Y'))

        if current_month == 1:
            current_month = 12
            current_year = current_year - 1
        else:
            current_month = current_month - 1

    pivot_list = pivot_list[:-1] + ')'        
    early_date = datetime(current_year, current_month, 20)

    sql =  '''with totals as (
        select count(*) as calls, to_char(connect_date, 'YYYY-MM') as mon,
        (select usage_subtype_name from ps_rating.USAGE_SUBTYPE_API_V where usage_subtype_id = r.usage_subtype_id) as Type
        from telecom.rated r
        where subscriber_id = %s
        and billed_on > %s
        group by to_char(connect_date, 'YYYY-MM'), usage_subtype_id
        )
        select * from totals
        pivot ( sum(calls) for mon in ''' + pivot_list + ')'
    
    context = {'totals': get_query_result(sql, (subscriber_id, early_date))
               ,'headings': headings}
    
    return context
