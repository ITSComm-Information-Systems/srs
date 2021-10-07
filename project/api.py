#from django.contrib.auth.models import User
from order.models import StorageInstance, ArcInstance, StorageRate, BackupDomain, BackupNode, ArcBilling, BackupDomain, Server, Database
from oscauth.models import LDAPGroup, LDAPGroupMember
from rest_framework import routers, viewsets
from . import serializers
from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.mail import EmailMessage
from apps.bom.models import Item, EstimateView, Material, MaterialLocation
from rest_framework.response import Response
import requests

from .models import Webhooks
import threading, time

def netboxEmails(request):
    tosend = Webhooks.objects.all().filter(emailed=False)
    if len(tosend) > 0:
        time.sleep(20)
        checkagain=Webhooks.objects.all().filter(emailed=False)
        if len(tosend) != len(checkagain):
            print('ongoing')
        else:
            success = list(Webhooks.objects.filter(emailed=False, success=True).values_list('preorder','name','added', 'skipped'))
            failed = list(Webhooks.objects.filter(emailed=False, success=False).values_list('preorder','name', 'issue'))
            success_message = "Inventory items added: \n"+"\n".join(["Preorder {} - Device {} - Number added: {} - Not added: {}".format(x[0],x[1],x[2],x[3]) for x in success])
            failed_message = "The following Devices were NOT added: \n"+"\n".join(["Preorder {} - Device {} - Issue: {}".format(x[0],x[1],x[2]) for x in failed])
            preorders = list(Webhooks.objects.filter(emailed=False).values_list('preorder', flat=True).distinct())
            try:
                preorders[preorders.index(None)] = 'no preorder'
            except:
                pass
            email = EmailMessage(
            subject='SRS Updated for preorder: '+ ", ".join(preorders),
            body=success_message + "\n" + failed_message,
            from_email='donotreply@example.com',
            to=[str(request.data['username']) + '@umich.edu'],
            reply_to=['another@example.com'],
            )
            email.send()
            checkagain.update(emailed=True)

class BomMaterialView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        status = request.data['data']['status']['value']
        pre_order = request.data['data']['custom_fields']['install_preorder_num']

        # Only process webhook if it's for WIFI/AP, staged, and has a pre_order number
        if request.data['data']['device_role']['name']=='WIFI/AP' and status =='staged' and pre_order != None:
            self.device_id = request.data['data']['id']
            self.location = request.data['data']['name']
            self.webhook = Webhooks(
                sender = request.data['username'],
                preorder = pre_order,
                device_id = self.device_id,
                name = self.location,  
            )
            # send get request to Netbox and get material
            try:
                self.estimate = EstimateView.objects.get(pre_order_number=pre_order)
                response = self.get_material(request)
                
            except Exception as e:
                self.webhook.issue = str(e)
                self.webhook.success = False
                self.webhook.save()
                response = 'No estimate found.'     

            threading.Thread(target=netboxEmails, args=[request]).start()
            content = {
                'status': response
            }

            return Response(content)
        else:
            content = {
                'status': 'Webhook not accepted'
            }

            return Response(content)
    
    def get_material(self, request):
        # Get inventory items from Netbox
        API_KEY = settings.NETBOX['NETBOX_KEY']
        request_address = settings.NETBOX['NETBOX_URL'] + '/api/dcim/inventory-items/?device_id=' + str(self.device_id)
        response = requests.get(request_address, headers={'Authorization': 'Token ' + API_KEY})
        response = response.json()

        unadded = []
        # Add all inventory items to data structure, if we have a Z-code for them
        for result in response['results']:
            # Z-code lookup
            try:
                item_code = Item.objects.get(manufacturer_part_number=result['name'])
            except:
                item_code = None
                unadded.append(result['name'])

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
        
        self.webhook.skipped=unadded
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
        self.webhook.added = len(self.inv_items)
        self.webhook.success = True
        self.webhook.save()

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