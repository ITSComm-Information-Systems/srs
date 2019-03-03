from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path

admin.AdminSite.site_header = 'OSC Administration'
admin.AdminSite.site_title = 'OSC Site Admin'

urlpatterns = [
    path('orders/', include('order.urls')),
    path('pages/', include('pages.urls')),
    path('oscauth/', include('oscauth.urls')),
    path('wismo/', include('wismo.urls')),
    path('su/', include('django_su.urls')),
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
