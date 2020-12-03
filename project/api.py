#from django.contrib.auth.models import User
from order.models import StorageInstance, ArcInstance, StorageRate, BackupDomain, BackupNode, ArcBilling, BackupDomain
from oscauth.models import LDAPGroup, LDAPGroupMember
from rest_framework import routers, viewsets
import rest_framework
from . import serializers

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

def get_view_class(model, serializer_class):
    name = model.__name__
    x = type(f'{name}ViewSet', (DefaultViewSet,), {})
    x.queryset = model.objects.all().order_by('id')
    if name == 'StorageRate':
        x.serializer_class = serializer_factory(model)
    else:
        x.serializer_class = serializer_class

    return x

def serializer_factory(model):
    name = model.__name__

    meta_attrs = {
        'model': model,
        'fields': '__all__'
    }
    meta = type('Meta', (), meta_attrs)

    return type(f'{name}Serializer', (rest_framework.serializers.ModelSerializer,), {'Meta': meta})

# Register URLs for API
router = routers.DefaultRouter()
router.register('storageinstances', get_view_class(StorageInstance, serializers.StorageInstanceSerializer))
router.register('storagerates', get_view_class(StorageRate, serializers.RateSerializer))
router.register('arcinstances', get_view_class(ArcInstance, serializers.ArcInstanceSerializer))
router.register('arcbilling', get_view_class(ArcBilling, serializers.ArcBillingSerializer))
router.register('backupdomains', get_view_class(BackupDomain, serializers.BackupDomainSerializer))
router.register('ldapgroups', LDAPGroupViewSet)
router.register('ldapgroupmembers', LDAPGroupMemberViewSet)
