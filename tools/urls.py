from django.urls import path

from django.conf.urls import include, url

urlpatterns = [
    path('voip/', include('tools.voip.urls')),
    path('costestimator/', include('tools.costestimator.urls'))
]