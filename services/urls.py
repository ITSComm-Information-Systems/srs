from django.urls import path
from order.views import Services, Workflow

from . import views

urlpatterns = [

    path('gcp/', views.Gcp.as_view()),
    path('aws/', views.Aws.as_view()),
    path('azure/', views.Azure.as_view()),

]