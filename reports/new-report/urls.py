from django.urls import path

from . import views
from reports.doc import views as doc

urlpatterns = [
	path('report/<str:type>/', doc.generate_report),
	path('', views.get_new),
    
]
