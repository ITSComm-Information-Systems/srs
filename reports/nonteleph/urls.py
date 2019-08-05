from django.urls import path

from . import views

urlpatterns = [
	path('report/', views.generate_report),
	path('', views.get_new),
    
]
