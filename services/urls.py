from django.urls import path
#from order.views import Services, Workflow

from . import views

urlpatterns = [

    # /services/aws/1/delete/
    # /services/aws/1/change/
    # /services/aws/add/
    # /services/aws/

    path('<str:service>/add/', views.ServiceRequestView.as_view()),
    path('<str:service>/', views.get_service_list),
    path('<str:service>/<int:id>/change/', views.ServiceChangeView.as_view()),
    path('<str:service>/<int:id>/delete/', views.ServiceDeleteView.as_view()),

]