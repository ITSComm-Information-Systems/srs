from django.urls import path
from order.views import Services, Workflow

from . import views

urlpatterns = [
    path('cart/<int:deptid>', views.Cart.as_view()),
    path('cart/', views.Cart.as_view()),
    path('status/<int:deptid>', views.Status.as_view()),

    path('addtocart/', views.add_to_cart),
    path('submit/', views.Submit.as_view()), 
    path('review/', views.Review.as_view()),
    path('services/', Services.as_view()),
    path('wf/<int:action_id>', Workflow.as_view()),

    path('chartcom/<int:deptid>', views.ManageChartcom.as_view()),
    path('chartcom/', views.ManageChartcom.as_view()),

    path('ajax/get_phone_location/<str:phone_number>', views.get_phone_location, name='get_phone_location'),

]
