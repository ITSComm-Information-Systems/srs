from django.conf import settings
from django.conf.urls import include, url, re_path
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static, serve
from . import views

#from django.contrib.auth.models import User
from order.models import StorageInstance, ArcInstance, StorageRate, BackupDomain, BackupNode, ArcBilling, BackupDomain
from rest_framework import routers, serializers, viewsets


admin.AdminSite.site_header = 'SRS Administration'
admin.AdminSite.site_title = 'SRS Site Admin'

class RateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['name','label','rate']
        read_only_fields = ['name', 'label', 'rate']
        model = StorageRate


class VolumeInstanceSerializer(serializers.ModelSerializer):  # Base Serializer for Storage Volumes

    owner = serializers.StringRelatedField()
    service = serializers.StringRelatedField()
    rate = RateSerializer(read_only=True)


class StorageInstanceSerializer(VolumeInstanceSerializer):

    class Meta:
        model = StorageInstance
        fields = ['id','name','owner','size','service','type','rate','shortcode','created_date','uid','ad_group','total_cost'
        ,'deptid','autogrow','flux']

class ArcBillingForInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArcBilling
        fields = ['size', 'shortcode']


class ArcInstanceSerializer(VolumeInstanceSerializer):
    hosts = serializers.StringRelatedField(many=True)
    shortcodes = ArcBillingForInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = ArcInstance
        fields = ['id','name','owner','size','service','type','rate','shortcodes', 'created_date','uid','ad_group','total_cost','hosts'
        ,'nfs_group_id','multi_protocol','sensitive_regulated','great_lakes','armis','lighthouse','globus','globus_phi','thunder_x']


class ArcBillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArcBilling
        fields = ['id', 'arc_instance', 'size', 'shortcode']


class ArcBillingViewSet(viewsets.ModelViewSet):
    queryset = ArcBilling.objects.all() 
    serializer_class = ArcBillingSerializer

    def get_queryset(self):
        arc_instance = self.request.query_params.get('arc_instance', None)

        print(arc_instance)

        if arc_instance is not None:
           self.queryset = self.queryset.filter(arc_instance__id=arc_instance)
        return self.queryset


class VolumeViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        name = self.request.GET.get('name')

        if name:
            queryset = self.serializer_class.Meta.model.objects.filter(name=name)
        else:
            queryset = self.serializer_class.Meta.model.objects.all().order_by('id')

        return queryset

class BackupDomainSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    nodes = serializers.StringRelatedField(many=True)

    class Meta:
        model = BackupDomain
        fields = ['id','name','shortcode','total_cost','cost_calculated_date','owner','days_extra_versions','days_only_version','versions_after_deleted','versions_while_exists','nodes']


class BackupDomainViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        name = self.request.GET.get('name')
 
        if name:
            queryset = self.serializer_class.Meta.model.objects.filter(name=name)
        else:
            queryset = self.serializer_class.Meta.model.objects.all().order_by('id')

        return queryset


class BackupDomainViewSet(VolumeViewSet):
    queryset = BackupDomain.objects.all()
    serializer_class = BackupDomainSerializer


class StorageViewSet(VolumeViewSet):
    queryset = StorageInstance.objects.all()
    serializer_class = StorageInstanceSerializer


class ArcViewSet(VolumeViewSet):
    queryset = ArcInstance.objects.all()
    serializer_class = ArcInstanceSerializer


class RateViewSet(VolumeViewSet):
    queryset = StorageRate.objects.all()
    serializer_class = RateSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'storageinstances', StorageViewSet)
router.register(r'storagerates', RateViewSet)
router.register(r'arcinstances', ArcViewSet)
router.register(r'arcbilling', ArcBillingViewSet)
router.register(r'backupdomains', BackupDomainViewSet)

urlpatterns = [

    re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
            }),

    path('oidc/', include('mozilla_django_oidc.urls')),
    path('orders/', include('order.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('oscauth.urls')),
    path('apps/', include('apps.urls')),
    #path('auth-api/', include('rest_framework.urls')),
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
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

