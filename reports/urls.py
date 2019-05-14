from django.urls import path

from django.conf.urls import include, url

urlpatterns = [
    path('tolls/', include('reports.toll.urls')),
    path('inventory/',include('reports.inventory.urls')),
    path('doc/', include('reports.doc.urls')),
    path('soc/', include('reports.soc.urls')),
    path('metrics/', include('reports.metrics.urls')),

]