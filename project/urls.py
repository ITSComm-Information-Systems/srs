from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from . import views

#from django.contrib.auth.models import User
from order.models import StorageInstance
from rest_framework import routers, serializers, viewsets


admin.AdminSite.site_header = 'SRS Administration'
admin.AdminSite.site_title = 'SRS Site Admin'


# Serializers define the API representation.
class StorageInstanceSerializer(serializers.HyperlinkedModelSerializer):
    hosts = serializers.StringRelatedField(many=True)

    class Meta:
        model = StorageInstance
        fields = ['id','name','owner','shortcode','uid','ad_group','deptid','size','type','flux','created_date','hosts']
 

# ViewSets define the view behavior.
class StorageViewSet(viewsets.ModelViewSet):

    queryset = StorageInstance.objects.all()
    serializer_class = StorageInstanceSerializer

    def get_queryset(self):
        name = self.request.GET.get('name')

        if name:
            queryset = StorageInstance.objects.filter(name=name)
        else:
            queryset = StorageInstance.objects.all()

        return queryset


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'storageinstances', StorageViewSet)

urlpatterns = [
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('orders/', include('order.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('oscauth.urls')),
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

