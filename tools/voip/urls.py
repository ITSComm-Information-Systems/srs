from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('building/', views.new_building),
    path('floor/', views.new_floor),
    path('room/', views.new_room),
    path('jack/', views.new_jack),
    path('confirm/',views.confirm),
    url(r'', views.get_voip),
    
]
