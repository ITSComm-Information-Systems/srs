from django.urls import path

from . import views

urlpatterns = [
    path('', views.e911),
    #path('report', views.generate)
]
