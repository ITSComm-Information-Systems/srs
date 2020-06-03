from django.urls import path

from django.conf.urls import include, url

urlpatterns = [
    path('rapid_time_entry/', include('apps.rapid_time_entry.urls'))
]