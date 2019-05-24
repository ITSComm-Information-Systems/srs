from django.urls import path

from . import views

urlpatterns = [
    path('cart/', views.get_cart),
    path('addtocart/', views.add_to_cart),
    path('submit/', views.submit_order),
    path('services/', views.get_services),
    path('wf/<int:action_id>', views.get_workflow),
]
