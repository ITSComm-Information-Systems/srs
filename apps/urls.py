from django.urls import path
from django.conf.urls import include, url

urlpatterns = [
    path('rte/', include('apps.rte.urls')),
    path('bom/', include('apps.bom.urls')),
    path('', include('pages.urls'))
]

