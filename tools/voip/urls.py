from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('jack/', views.get_jack),
    url(r'', views.get_voip),
    
]
