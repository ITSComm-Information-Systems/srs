from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from . import views

admin.AdminSite.site_header = 'OSC Administration'
admin.AdminSite.site_title = 'OSC Site Admin'

urlpatterns = [
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('orders/', include('order.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('oscauth.urls')),
    path('admin/', admin.site.urls),
    path('reports/',include('reports.urls')),
    path('cf_get_dept/', views.get_dept),
    path('chartchange/ajax/', views.change_dept),
    path('chartchange/old-cf/', views.get_cf_data),
    path('chartchange/<str:dept_parm>/change-dept/to<str:change_dept>/', views.chartchange),
    path('chartchange/<str:dept_parm>/change-dept/', views.change_dept),
    path('chartchange/<str:dept_parm>/', views.chartchange),
    path('chartchange/', views.chartchange),
    path('', include('pages.urls')),
    path('tools/',include('tools.urls'))
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)