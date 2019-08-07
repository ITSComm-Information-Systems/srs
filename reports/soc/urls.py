from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_soc),
    path('report', views.generate)
]
