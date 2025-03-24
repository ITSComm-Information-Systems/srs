
from django.contrib.auth.decorators import permission_required

from django.shortcuts import render



@permission_required('can_manage')
def e911(request):
    return render(request, 'e911.html',
                        {'title': 'Zoom Phone Addresses',
                         'notices': 	['foo','bar']
                        })