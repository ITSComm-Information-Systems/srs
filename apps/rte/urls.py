from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
	path('single-tech/review/', views.single_review),
    path('single-tech/', views.single_tech),
    path('multiple-tech/', views.multiple_tech),
    path('update/view-times/', views.view_times),
    path('update/', views.update),
    url(r'', views.load_rte),
    
]
