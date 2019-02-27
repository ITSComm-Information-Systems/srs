from django.urls import path

from . import views

urlpatterns = [
    path('cart/', views.index, name='index'),
    path('phone/', views.phone, name='order_phone.html'),
]
