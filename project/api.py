#from django.contrib.auth.models import User
from order.models import StorageInstance, ArcInstance, StorageRate, BackupDomain, BackupNode, ArcBilling, BackupDomain, Server, Database
from oscauth.models import LDAPGroup, LDAPGroupMember
from rest_framework import routers, viewsets
from . import serializers

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.mail import EmailMessage
from apps.bom.models import Item, EstimateView, Material, MaterialLocation
from rest_framework.response import Response
import requests
from .models import Webhooks
# add timer module here
import threading, sched, time

scheduler = sched.scheduler(time.time, time.sleep)

def print_event(name):
    print('EVENT:', time.time(), name)

scheduler.enter(2, 1, print_event, ('first',))
scheduler.enter(3, 1, print_event, ('second',))

scheduler.run()
# def netboxEmails():
#     tosend = Webhooks.objects.filter(notified=False)

#     if len(tosend) > 0:


#         email = EmailMessage(
#         subject='SRS Updated',
#         body='items from Netbox added',
#         from_email='donotreply@example.com',
#         to=[str(request.data['username'])+'@umich.edu'],
#         reply_to=['another@example.com'],
#         )
#         email.send()

# thread = threading.Thread(target=netboxEmails)


class BomMaterialView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only process webhook if it's for WIFI/AP, not anything else
        if request.data['data']['device_role']['name']=='WIFI/AP':
            status = request.data['data']['status']['value']
            self.device_id = request.data['data']['id']
            self.location = request.data['data']['name']
            pre_order = request.data['data']['custom_fields']['install_preorder_num']

            webhook = Webhooks()
            webhook.sender = request.data['username']
            webhook.device_id = self.device_id
            webhook.notified = False

            # If status = staged, pre_order=estimate number, send get request to Netbox and get material
            if status == 'staged' and pre_order != '' :
                try:
                    self.estimate = EstimateView.objects.get(pre_order_number=pre_order)
                    response = self.get_material(request)
                except Exception as e:
                    webhook.issue = str(e)
                    webhook.success = False
                    webhook.save()
                    response = 'No estimate found.'
            else:
                response = 'Waiting for staged status or pre-order-number.'
                webhook.issue = 'status or preorder issue'
                webhook.success = False
                webhook.save()            

            content = {
                'status': response
            }

            return Response(content)
    
    def get_material(self, request):
        # Get inventory items from Netbox
        API_KEY = '0123456789abcdef0123456789abcdef01234567'
        request_address = 'https://netbox-wdb.dev.infra.apps.it.umich.edu/api/dcim/inventory-items/?device_id=' + str(self.device_id)
        response = requests.get(request_address, headers={'Authorization': 'Token ' + API_KEY})
        response = response.json()

        # Add all inventory items to data structure, if we have a Z-code for them
        for result in response['results']:
            # Z-code lookup
            try:
                item_code = Item.objects.get(manufacturer_part_number=result['name'])
            except:
                item_code = None

            # Add existing item
            if item_code:
                # If item not already in list, add it
                if not any(d['code'] == item_code.code for d in self.inv_items):
                    item = {
                        'location': self.location,
                        'code': item_code.code,
                        'quantity': 1
                    }
                    self.inv_items.append(item)
                # Or increase quantity
                else:
                    item = next((i for i in self.inv_items if i['code'] == item_code.code), None)
                    item['quantity'] = item['quantity'] + 1
        
        # Add items in data structure to estimate
        result = self.add_items(request)
        return result
    
    def add_items(self, request):
        print('add_items inventory items:'+str(self.inv_items))
        # Get rid of all existing items
        try:
            location = MaterialLocation.objects.get(estimate_id=self.estimate.id, name=self.location)
            materials = Material.objects.filter(material_location=location.id)
            for mat in materials:
                mat.delete()
        except Exception as e:
            # probably no existing items
            print("exception in add_items:"+str(e))

        # Add all items from Netbox
        for item in self.inv_items:
            mat = Material()
            mat.set_create_audit_fields(request.data['username'])
            mat.item_code = item['code']
            mat.quantity = item['quantity']
            new_location = MaterialLocation.objects.get_or_create(estimate_id=self.estimate.id, name=item['location'])
            mat.material_location = new_location[0]
            mat.save()

        webhook.success = True
        webhook.save()

        return 'Response premitted.'
    
    def __init__(self):
        self.device_id = ''
        self.location = ''
        self.inv_items = []
        self.estimate = ''

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
            field = parm.split('__')[0]

            if hasattr(self.serializer_class.Meta.model, field):
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
router.register('storagerates', viewset_factory(StorageRate, serializers.StorageRateSerializer))
router.register('arcinstances', viewset_factory(ArcInstance, serializers.ArcInstanceSerializer))
router.register('arcbilling', viewset_factory(ArcBilling, serializers.ArcBillingSerializer))
router.register('backupdomains', viewset_factory(BackupDomain, serializers.BackupDomainSerializer))
#router.register('server', viewset_factory(Server, serializers.ServerSerializer))
router.register('server', viewset_factory(Server))
router.register('database', viewset_factory(Database, serializers.DatabaseSerializer))
router.register('ldapgroups', LDAPGroupViewSet)
router.register('ldapgroupmembers', LDAPGroupMemberViewSet)