from django.conf import settings
from django.conf.urls import include, url, re_path
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static, serve
from . import views

#from django.contrib.auth.models import User
from order.models import StorageInstance, ArcInstance, StorageRate, BackupDomain, BackupNode, ArcBilling, BackupDomain
from oscauth.models import LDAPGroup, LDAPGroupMember
from rest_framework import routers, viewsets
from . import serializers

admin.AdminSite.site_header = 'SRS Administration'
admin.AdminSite.site_title = 'SRS Site Admin'


class LDAPViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        username = self.request.GET.get('username')
        ldap_group = self.request.GET.get('ldap_group')
        name = self.request.GET.get('name')
        active = self.request.GET.get('active')

        if username:
            queryset = self.serializer_class.Meta.model.objects.filter(username=username)
        elif ldap_group:
            queryset = self.serializer_class.Meta.model.objects.filter(ldap_group__name=ldap_group)
        elif name:
            queryset = self.serializer_class.Meta.model.objects.filter(name=name)
        elif active:
            queryset = self.serializer_class.Meta.model.objects.filter(active=active)
        else:
            queryset = self.serializer_class.Meta.model.objects.all().order_by('id')

        return queryset

class LDAPGroupViewSet(LDAPViewSet):
    queryset = LDAPGroup.objects.all()
    serializer_class = serializers.LDAPGroupSerializer

class LDAPGroupMemberViewSet(LDAPViewSet):
    queryset = LDAPGroupMember.objects.all()
    serializer_class = serializers.LDAPGroupMemberSerializer

class DefaultViewSet(viewsets.ModelViewSet):
    queryset = StorageRate.objects.all()

    def get_queryset(self):
        queryset = self.serializer_class.Meta.model.objects.all().order_by('id')

        kwargs = {}

        for parm, val in self.request.GET.items():
            if parm != 'page':
                kwargs[parm] = val

        queryset = queryset.filter(**kwargs)
        
        return queryset

class StorageInstanceViewSet(DefaultViewSet):
    queryset = StorageInstance.objects.all()
    serializer_class = serializers.StorageInstanceSerializer

class ArcInstanceViewSet(DefaultViewSet):
    serializer_class = serializers.ArcInstanceSerializer
    queryset = ArcInstance.objects.all()

class RateViewSet(DefaultViewSet):
    serializer_class = serializers.RateSerializer
    queryset = StorageRate.objects.all()

class ArcBillingViewSet(DefaultViewSet):
    serializer_class = serializers.ArcBillingSerializer
    queryset = ArcBilling.objects.all()

class BackupDomainViewSet(DefaultViewSet):
    serializer_class = serializers.BackupDomainSerializer
    queryset = BackupDomain.objects.all()

# Register URLs for API
router = routers.DefaultRouter()
router.register('storageinstances', StorageInstanceViewSet)
router.register('storagerates', RateViewSet)
router.register('arcinstances', ArcInstanceViewSet)
router.register('arcbilling', ArcBillingViewSet)
router.register('backupdomains', BackupDomainViewSet)
router.register('ldapgroups', LDAPGroupViewSet)
router.register('ldapgroupmembers', LDAPGroupMemberViewSet)


urlpatterns = [

    re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
            }),

    path('oidc/', include('mozilla_django_oidc.urls')),
    path('orders/', include('order.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('oscauth.urls')),
    path('apps/', include('apps.urls')),
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('reports/',include('reports.urls')),
    path('chartchange/ajax/', views.change_dept),
    path('chartchange/old-cf/', views.get_cf_data),
    path('chartchange/update-table/', views.get_users),
    path('chartchange/submit/', views.submit),
    path('chartchange/', views.chartchange),
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

