from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
	path('single-tech/submitted/', views.single_submit),
    path('single-tech/', views.single_tech),
    path('multiple-tech/get-assigned-group/', views.get_assigned_group),
    path('multiple-tech/', views.multiple_tech),
    path('update/view-times/', views.view_times),
    path('update/', views.update),
    url(r'', views.load_rte),
    
]
