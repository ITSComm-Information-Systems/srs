from django.urls import path
from order.views import Services, Workflow

from . import views

urlpatterns = [
    path('cart/<int:deptid>', views.UserCart.as_view()),
    path('cart/', views.UserCart.as_view()),
    path('addtocart/', views.add_to_cart),
    path('submit/', views.submit_order),
    path('services/', Services.as_view()),
    path('wf/<int:action_id>', Workflow.as_view()),
]
