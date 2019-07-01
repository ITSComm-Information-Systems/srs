from django.urls import path

from . import views

urlpatterns = [
	path('report/tsr/', views.show_tsr),
	path('report/detail/', views.show_detail),
	path('report/', views.generate_report),
    path('', views.get_doc),
    
]
