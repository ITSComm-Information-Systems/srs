#from django.contrib.auth.models import User
from order.models import StorageInstance, ArcInstance, StorageRate, BackupDomain, BackupNode, ArcBilling, BackupDomain
from oscauth.models import LDAPGroup, LDAPGroupMember
from rest_framework import routers, viewsets
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

def viewset_factory(model, serializer_class=None):
    name = model.__name__
    x = type(f'{name}ViewSet', (DefaultViewSet,), {})
    x.queryset = model.objects.all().order_by('id')

    if serializer_class:
        x.serializer_class = serializer_class
    else:
        x.serializer_class = serializers.serializer_factory(model)

    return x


# Register URLs for API
router = routers.DefaultRouter()
router.register('storageinstances', viewset_factory(StorageInstance, serializers.StorageInstanceSerializer))
router.register('storagerates', viewset_factory(StorageRate))
router.register('arcinstances', viewset_factory(ArcInstance, serializers.ArcInstanceSerializer))
router.register('arcbilling', viewset_factory(ArcBilling, serializers.ArcBillingSerializer))
router.register('backupdomains', viewset_factory(BackupDomain, serializers.BackupDomainSerializer))
router.register('ldapgroups', LDAPGroupViewSet)
router.register('ldapgroupmembers', LDAPGroupMemberViewSet)
