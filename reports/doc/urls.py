from django.urls import path

from . import views

urlpatterns = [
	path('select-cf/', views.select_cf),
	path('report/detail/', views.show_detail),
	path('report/', views.generate_report),
    path('', views.get_doc),
    
]
