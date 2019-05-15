from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

admin.AdminSite.site_header = 'OSC Administration'
admin.AdminSite.site_title = 'OSC Site Admin'

urlpatterns = [
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('orders/', include('order.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('oscauth.urls')),
    path('admin/', admin.site.urls),
    path('reports/',include('reports.urls')),
    path('', include('pages.urls')),
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)