from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from reports.models import DepartmentalTelephoneServiceMetricsClickLog as DownloadLog

@csrf_exempt
def log_click(request):
    username = request.user.username
    log_event = DownloadLog(
		clicked_by=username
	)
    log_event.save()
    return HttpResponse("logged", status=200)