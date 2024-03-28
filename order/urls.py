from django.urls import path
from order.views import Services, Workflow

from . import views

urlpatterns = [
    path('cart/<int:deptid>', views.Cart.as_view()),
    path('cart/', views.Cart.as_view()),
    path('status/<int:deptid>', views.Status.as_view()),

    path('deletefromcart/', views.delete_from_cart),
    path('addtocart/', views.add_to_cart),
    path('sendemail/', views.send_email),
    path('submit/', views.Submit.as_view()), 
    path('review/', views.Review.as_view()),
    path('services/<int:group_id>', Services.as_view()),
    path('wf/<int:action_id>', Workflow.as_view()),
    path('database/<int:instance_id>', views.DatabaseView.as_view()),
    path('server/<int:instance_id>/<str:action>/', views.ServerView.as_view()),

    path('detail/<int:order_id>', views.get_order_detail),
    path('integration/<int:order_id>', views.Integration.as_view()),
    path('integration/', views.get_order_list),

    path('chartcom/<int:deptid>', views.ManageChartcom.as_view()),
    path('chartcom/', views.ManageChartcom.as_view()),

    path('ajax/get_phone_location/<str:phone_number>', views.get_phone_location, name='get_phone_location'),
    path('ajax/get_phone_information/<str:uniqname>', views.get_phone_information, name='get_phone_information'),
    path('ajax/send_tab_data/', views.send_tab_data, name='send_tab_data'),

]
