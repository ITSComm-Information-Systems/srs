from django.conf import settings
from django.conf.urls import include, url, re_path
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static, serve
from . import views
from . import api

admin.AdminSite.site_header = 'SRS Administration'
admin.AdminSite.site_title = 'SRS Site Admin'


urlpatterns = [

    re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
            }),

    path('oidc/', include('mozilla_django_oidc.urls')),
    path('orders/', include('order.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('oscauth.urls')),
    path('apps/', include('apps.urls')),
    path('api/', include(api.router.urls)),
    path('api/bommaterial/', api.BomMaterialView.as_view()),
    path('admin/', admin.site.urls),
    path('reports/',include('reports.urls')),
    path('chartchange/ajax/', views.change_dept),
    path('chartchangedept/ajax/', views.change_dept_new),
    path('chartchange/old-cf/', views.get_cf_data),
    path('chartchange/update-table/', views.get_users),
    path('chartchange/submit/', views.submit),
    path('chartchangedept/submit/', views.submit_new), # AJAX
    path('chartchange/', views.chartchange),
    path('chartchangedept/', views.chartchangedept),
    path('managerapproval/', views.managerapproval),
    path('managerapprovalinit/', views.managerapprovalinit), # AJAX
    path('', views.homepage),
    path('', include('pages.urls')),
    path('tools/',include('tools.urls'))
]

if settings.SRS_OUTAGE:
    from django.views.generic import TemplateView 
    urlpatterns = [
        #re_path(r'^', views.homepage, name='bio')

        re_path(r'^', TemplateView.as_view(template_name="outage.html"))
        #re_path('<str:pagename>', views.index, name='index'),
    ]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

