from django.urls import path
#from order.views import Services, Workflow

from . import views

urlpatterns = [

    # /services/aws/1/delete/
    # /services/aws/1/change/
    # /services/aws/add/
    # /services/aws/


    path('<str:service>/add/', views.ServicesView.as_view()),

    #path('gcp/add/', views.Gcp.as_view()),
    #path('aws/add/', views.Aws.as_view()),
    #path('azure/add/', views.Azure.as_view()),


    path('<str:service>/', views.get_service_list),

    path('<str:service>/<int:id>/change/', views.change_request),

    #path('aws/add/', views.ServiceList.as_view()),
    #path('azure/add/', views.ServiceList.as_view()),

]