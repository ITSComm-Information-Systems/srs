from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from . import views

#from django.contrib.auth.models import User
from order.models import StorageInstance, ArcInstance, StorageRate
from rest_framework import routers, serializers, viewsets


admin.AdminSite.site_header = 'SRS Administration'
admin.AdminSite.site_title = 'SRS Site Admin'

class RateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['name','label','rate']
        model = StorageRate


class VolumeInstanceSerializer(serializers.ModelSerializer):  # Base Serializer for Storage Volumes

    owner = serializers.StringRelatedField()
    service = serializers.StringRelatedField()
    rate = RateSerializer(read_only=True)


class StorageInstanceSerializer(VolumeInstanceSerializer):

    class Meta:
        model = StorageInstance
        fields = ['name','owner','size','service','type','rate','shortcode','created_date','uid','ad_group','total_cost'
        ,'deptid','autogrow','flux']


class ArcInstanceSerializer(VolumeInstanceSerializer):
    hosts = serializers.StringRelatedField(many=True)

    class Meta:
        model = ArcInstance
        fields = ['name','owner','size','service','type','rate','shortcode','created_date','uid','ad_group','total_cost','hosts'
        ,'nfs_group_id','sensitive_regulated','great_lakes','armis','lighthouse','globus','globus_phi','thunder_x']


class VolumeViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        name = self.request.GET.get('name')

        if name:
            queryset = self.serializer_class.Meta.model.objects.filter(name=name)
        else:
            queryset = self.serializer_class.Meta.model.objects.all().order_by('id')

        return queryset


class StorageViewSet(VolumeViewSet):
    queryset = StorageInstance.objects.all()
    serializer_class = StorageInstanceSerializer


class ArcViewSet(VolumeViewSet):
    queryset = ArcInstance.objects.all()
    serializer_class = ArcInstanceSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'storageinstances', StorageViewSet)
router.register(r'arcinstances', ArcViewSet)

urlpatterns = [
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

