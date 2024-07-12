from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls.static import static, serve
from . import views
from . import api

admin.AdminSite.site_header = 'SRS Administration'
admin.AdminSite.site_title = 'SRS Site Admin'

handler404 = views.handle_custom_404
handler500 = views.handle_custom_500

urlpatterns = [

    re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
            }),

    path('oidc/', include('mozilla_django_oidc.urls')),
    path('orders/', include('order.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('oscauth.urls')),
    path('apps/', include('apps.urls')),
    path('softphone/', include('softphone.urls')),
    path('services/', include('services.urls')),
    path('api/', include(api.router.urls)),
    path('api/bommaterial/', api.BomMaterialView.as_view()),
    path('api/tollupload/', api.TollUploadView.as_view()),
    path('admin/', admin.site.urls),
    path('reports/',include('reports.urls')),
    path('sample/', views.SampleView.as_view()),
    path('uniqname/', views.get_uniqname),
    path('chartchange/ajax/', views.change_dept_1),
    path('chartchangedept/ajax/', views.change_dept_3),
    path('chartchange/old-cf/', views.get_cf_data),
    path('chartchange/update-table/', views.get_users),
    path('chartchange/submit/', views.submit),
    path('chartchangedept/submit/', views.submit_new), # AJAX
    path('chartchange/', views.chartchange),
    path('chartchangedept/', views.chartchangedept),
    path('chartchangeoptions/', views.chartchangeoptions), #chartfield options home page
    path('managerapproval/', views.managerapproval),
    path('managerapprovalinit/', views.managerapprovalinit), # AJAX
    path('managerapproval/submit/', views.managerapprovalsubmit), # AJAX
    #path('namechange/', views.NameChange.as_view()),
    path('', views.homepage),
    path('', include('pages.urls')),
    path('tools/',include('tools.urls')),
    #path('testtest/',views.raise404)

] 

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

