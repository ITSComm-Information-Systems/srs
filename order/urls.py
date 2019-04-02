from django.urls import path

from . import views

urlpatterns = [
    path('cart/', views.cart),
    path('addtocart/', views.add_to_cart),
    path('services/', views.get_services),
    path('wf/<int:action_id>', views.get_workflow),
 
    path('ajax/load-actions/', views.load_actions, name='ajax_load_actions'),  # <-- this one here

    path('wf/<int:action_id>', views.get_workflow),


]
