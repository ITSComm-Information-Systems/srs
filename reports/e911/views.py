
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from softphone.models import ZoomAPI
from oscauth.models import AuthUserDept
from project.utils import download_csv_from_queryset


@permission_required('oscauth.can_order')
def e911(request):

    department_list = list(AuthUserDept.objects.filter(user=request.user, group_id__in=[3, 4]).values_list('dept', flat=True))
    phone_numbers = ZoomAPI.objects.filter(dept_id__in=department_list, default_address=True).order_by('username').values('username','dept_id','phone_number')

    if request.GET.get('file') == 'CSV' and len(phone_numbers) > 0:
        return download_csv_from_queryset(phone_numbers, file_name='e911_addresses')

    return render(request, 'e911.html',

                        {'title': 'Zoom Phone Addresses',
                         'department_list': department_list,
                         'phone_numbers': phone_numbers
                        })

