from django.urls import path

from django.conf.urls import include, url

urlpatterns = [
    path('voip/', include('tools.voip.urls')),
    path('rte/', include('tools.rte.urls')),
    path('costestimator/', include('tools.costestimator.urls'))
]