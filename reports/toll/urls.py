from django.urls import path

from . import views

urlpatterns = [
    path('download/csv/<bill_date>/<deptid>/', views.download_CSV),
    path('download/pdf/<bill_date>/<deptid>/', views.download_PDF),
    path('download/cond-pdf/<bill_date>/<deptid>/', views.download_cond_PDF),
	path('', views.select),
    path('downloads', views.generate),
    path('download/log/', views.log_report_download),
]
