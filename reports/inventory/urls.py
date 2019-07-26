from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_inventory),
    path('report', views.make_report)
]
