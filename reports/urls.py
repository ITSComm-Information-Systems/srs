from django.urls import path
from . import views

from django.conf.urls import include

urlpatterns = [
    path('tolls/', include('reports.toll.urls')),
    path('inventory/',include('reports.inventory.urls')),
    path('doc/', include('reports.doc.urls')),
    path('soc/', include('reports.soc.urls')),
    path('metrics/', include('reports.metrics.urls')),
    path('nonteleph/', include('reports.nonteleph.urls')),
    path('usage/', include('reports.usage.urls')),
    path('e911/', include('reports.e911.urls')),
]