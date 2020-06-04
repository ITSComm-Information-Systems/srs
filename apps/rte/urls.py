from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
	path('single-tech/submitted/', views.single_submit),
    path('single-tech/', views.single_tech),
    path('multiple-tech/get-assigned-group/', views.get_assigned_group),
    path('multiple-tech/submitted/', views.multiple_submit),
    path('multiple-tech/', views.multiple_tech),
    path('update/select-times/', views.select_times),
    path('update/', views.update),
    path('view-time/display/', views.view_time_display),
    path('view-time/', views.view_time_load),
    url(r'', views.load_rte),
    
]
