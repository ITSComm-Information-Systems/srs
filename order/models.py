from typing import Sequence
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.postgres.fields import JSONField
from django.contrib.admin.models import LogEntry, ADDITION
from django.db import models
from django.forms.fields import DecimalField
from ldap3.protocol.rfc4511 import Control
from oscauth.models import Role, LDAPGroup, LDAPGroupMember
from project.pinnmodels import UmOscPreorderApiV
from project.integrations import MCommunity, TDx
from project.models import ShortCodeField, Choice
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.db import connections
from django.template.loader import render_to_string
from ast import literal_eval
import json, io, os, requests
import cx_Oracle
from django.core.exceptions import ValidationError
from oscauth.utils import get_mc_user, get_mc_group
from decimal import Decimal
from django.utils.functional import cached_property


if settings.ENVIRONMENT == 'Production':
    TDX_URL = 'https://teamdynamix.umich.edu/TDNext/Apps/31/Tickets/TicketDet.aspx?TicketID='
else:
    TDX_URL = 'https://teamdynamix.umich.edu/SBTDNext/Apps/31/Tickets/TicketDet?TicketID='

class Configuration(models.Model):   #Common fields for configuration models
    name = models.CharField(max_length=20)
    label = models.CharField(max_length=100)
    display_seq_no = models.PositiveIntegerField()

    def __str__(self):
        return self.label

    class Meta:
        abstract = True 


class Step(Configuration):
    FORM_CHOICES = (
        ('', ''),
        ('TabForm', 'Base Form'),
        ('PhoneLocationForm', 'Phone Location'),
        ('EquipmentForm', 'Equipment'),
        ('NewLocationForm', 'New Location'),
        ('AddlInfoForm', 'Additional Information'),
        ('ReviewForm', 'Review'),
        ('ChartfieldForm', 'Chartfield'),
        ('RestrictionsForm', 'Restrictions'),
        ('FeaturesForm', 'Features'),
        ('StaticForm', 'Static Page'),
        ('AuthCodeForm', 'Auth Codes'),
        ('AuthCodeCancelForm', 'Auth Codes'),
        ('CMCCodeForm', 'CMC Codes'),
        ('ProductForm', 'Quantity Model'),
        ('ContactCenterForm', 'Contact Center'),
        ('BillingForm', 'Billing'),
        ('VoicemailForm', 'Voicemail'),
        ('DetailsCIFSForm', 'CIFS Details'),
        ('DetailsNFSForm', 'NFS Details'),
        ('AccessCIFSForm', 'CIFS Access'),
        ('AccessNFSForm', 'NFS Access'),
        ('BillingStorageForm', 'Billing'),
        ('BackupDetailsForm', 'Backup Details'),
        ('VolumeSelectionForm', 'Volume Selection'),
        ('SubscriptionSelForm', 'Subscription Selection'),
        ('DatabaseTypeForm', 'Database Type'),
        ('DatabaseConfigForm', 'Database Configuration'),
        ('ServerInfoForm', 'Server Info'),
        ('ServerSupportForm', 'Server Support'),
        ('ServerSpecForm', 'Server Specification'),
        ('ServerDataForm', 'Server Data Sensitivity'),
        ('DataDenForm', 'Data Den Form')
    )

    custom_form = models.CharField(blank=True, max_length=20, choices=FORM_CHOICES)
    progressive_disclosure = models.BooleanField(default=False)

class Element(Configuration):
    ELEMENT_CHOICES = (
        ('', ''),
        ('Radio', 'Radio'),
        ('ST', 'String'),
        ('Select', 'Select'),
        ('List', 'List'),
        ('NU', 'Number'),
        ('Chart', 'Chartcom'),
        ('Label', 'Label'),
        ('Checkbox', 'Checkbox'),
        ('McGroup', 'MCommunity Group'),
        ('MyGroups', 'Users MCommunity Group'),
        ('ShortCode', 'Short Code'),
        ('Phone', 'Phone Number'),
        ('Uniqname', 'Uniqname'),
        ('HTML', 'Static HTML'),
        ('EmailField', 'Email'),
    )
    label = models.TextField()
    description = models.TextField(blank=True)
    help_text = models.TextField(blank=True)
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=ELEMENT_CHOICES)
    attributes = models.CharField(blank=True, max_length=1000)
    arguments = models.JSONField(blank=True, default=dict)
    display_condition = models.CharField(blank=True, max_length=100)
    target = models.CharField(max_length=80, blank=True, null=True)


class ProductCategory(Configuration):
    
    class Meta:
        verbose_name_plural = "Product Categories"


class Product(Configuration):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    active = models.BooleanField(default=True)
    picture = models.FileField(upload_to='pictures',blank=True, null=True)


class ServiceGroup(Configuration):
    active = models.BooleanField(default=True)


class Service(Configuration):
    active = models.BooleanField(default=True)
    group = models.ForeignKey(ServiceGroup, on_delete=models.CASCADE)
    routing = models.JSONField(default=dict)


class FeatureCategory(models.Model):
    name = models.CharField(max_length=20)
    label = models.CharField(max_length=100)
    display_seq_no = models.PositiveIntegerField()

    def __str__(self):
        return self.label
    
    class Meta:
        verbose_name_plural = "Feature Categories"


class FeatureType(models.Model):
    name = models.CharField(max_length=20)
    label = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.label

    
class Feature(Configuration):
    TYPE_CHOICES = (
        ('STD', 'Standard'),
        ('OPT', 'Optional'),
        ('SPD', 'Speed Call'),
        ('VM', 'Voice Mail'),
    )

    category = models.ManyToManyField(FeatureCategory)
    #type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    type = models.ForeignKey(FeatureType, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    additional_info = models.TextField(blank=True)
    active = models.BooleanField(default=True)


class Restriction(Configuration):
    category = models.ManyToManyField(FeatureCategory)


class ChargeType(Configuration):
    pass


class Action(Configuration):
    ROUTE_CHOICES = (
        ('P', 'Preorder'),
        ('I', 'Incident'),
        ('E', 'Email'),
    )

    TYPE_CHOICES = (
        ('A', 'Add'),
        ('M', 'Modify'),
        ('D', 'Disconnect'),
        ('E', 'Equipment'),
    )
    cart_label = models.CharField(max_length=100, blank=True, null=True)
    use_cart = models.BooleanField(default=True)
    use_ajax = models.BooleanField(default=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='A')
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)    
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    charge_types = models.ManyToManyField(ChargeType)
    steps = models.ManyToManyField(Step)
    override = models.JSONField(null=True, blank=True)
    route = models.CharField(max_length=1, choices=ROUTE_CHOICES, default='P')
    destination = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.label 

    def get_tab_list(self):
        #tabs = Step.objects.filter(action = action_id).order_by('display_seq_no')
        tab_list = list(Step.objects.filter(action=self.id).order_by('display_seq_no').values('name'))

        return tab_list

    def get_hidden_fields(self):
        try:
            return self.override['hide']
        except:
            return []


class Constant(models.Model):
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    field = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.field 


class Chartcom(models.Model):
    fund = models.CharField(max_length=30)
    dept = models.CharField(max_length=30)
    program = models.CharField(max_length=30)
    class_code = models.CharField(max_length=30)
    project_grant = models.CharField(max_length=30)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.fund

    @property
    def account_number(self):
        account_number = self.fund + '-' + self.dept + '-' + self.program + '-' + self.class_code
        if self.project_grant:
            account_number = account_number + '-' + self.project_grant

        return account_number

    def get_user_chartcoms(self):
        chartcom_list = UserChartcomV.objects.filter(user=self).order_by('name')
        #user_chartcoms = []
        
        #for chartcom in chartcom_list:
        #    user_chartcoms.append((chartcom.chartcom_id, chartcom.name, chartcom.dept, chartcom.account_number))

        return chartcom_list

    def get_user_chartcom_depts(self):
        dept_list = UserChartcomV.objects.filter(user=self).order_by('dept').values('dept').distinct()
        user_chartcom_depts = []
        


        for chartcom in dept_list:
            user_chartcom_depts.append((chartcom.get('dept')))

        return user_chartcom_depts

    def get_user_chartcoms_for_dept(self, dept):

        if self.has_perm('can_order_all'):
            chartcom_list = Chartcom.objects.filter(dept=dept)
            cc_list = []
            for cc in chartcom_list:
                item = vars(cc)
                item['account_number'] = cc.account_number
                delattr(cc, '_state')
                cc_list.append(item)
                
            chartcom_list = cc_list
            
        else:
            chartcom_list = list(UserChartcomV.objects.filter(user=self, dept=dept).order_by('name').values())

        return chartcom_list


class UserChartcomV(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    chartcom = models.ForeignKey(Chartcom, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=20, blank=True, primary_key=True)
    dept = models.CharField(max_length=30)
    account_number = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'order_user_chartcom_v'


class LogItem(models.Model):
    transaction = models.CharField(max_length=20)
    local_key = models.CharField(max_length=20, blank=True)
    remote_key = models.CharField(max_length=20, blank=True)
    create_date = models.DateTimeField('Date Created', auto_now_add=True)
    level = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)

    def add_log_entry(self, transaction, local_key, descr):
        self.transaction = transaction
        self.local_key = local_key
        self.remote_key = 23432
        self.level = 'Info'
        self.description = descr
        self.save()
    

class StorageRate(Configuration):
    TYPE_CHOICES = (
        ('NFS', 'NFS'),
        ('CIFS', 'CIFS'),
    )

    UNIT_OF_MEASURE_CHOICES = (
        ('GB', 'Gigabytes'),
        ('TB', 'Terabytes'),
    )

    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    type = models.CharField(max_length=4, default='NFS', choices=TYPE_CHOICES)
    rate = models.DecimalField(max_digits=8, decimal_places=6)
    unit_of_measure = models.CharField(max_length=2, default='GB', choices=UNIT_OF_MEASURE_CHOICES)

    def __str__(self):
        return self.label

    def get_total_cost(self, size):
        total_cost = round(self.rate * int(size), 2)
        return total_cost


class StorageOwner(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StorageMember(models.Model):
    storage_owner = models.ForeignKey(StorageOwner, on_delete=models.CASCADE)
    username = models.CharField(max_length=8)


class Volume(models.Model):
    TYPE_CHOICES = (
        ('NFS', 'NFS'),
        ('CIFS', 'CIFS'),
    )

    name = models.CharField(max_length=100)
    owner = models.ForeignKey(LDAPGroup, on_delete=models.CASCADE, null=True)
    size = models.PositiveIntegerField()
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    type = models.CharField(max_length=4, default='NFS', choices=TYPE_CHOICES)
    rate = models.ForeignKey(StorageRate, on_delete=models.CASCADE)    
    shortcode = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=timezone.now)
    uid = models.PositiveIntegerField(blank=True, null=True)
    ad_group = models.CharField(max_length=100, null=True, blank=True)

    @property
    def total_cost(self):
        total_cost = round(self.rate.rate * int(self.size), 2)
        return total_cost

    def __str__(self):
        return self.name

    def get_checkboxes(self):
        checkboxes = []
        for field in self._meta.get_fields():
            if type(field) == models.BooleanField:
                if getattr(self, field.name):
                    checkboxes.append(field.name)

        return checkboxes

    def get_tickets(self):
        actions = Action.objects.filter(service=self.service).values_list('id', flat=True)
        tickets = Item.objects.filter(data__instance_id=self.id
            , external_reference_id__isnull=False
            , data__action_id__in=actions)
        ticket_list = []
        for ticket in tickets: 
            ticket_list.append({'id': ticket.external_reference_id
                              , 'url': f'{TDX_URL}{ticket.external_reference_id}'
                              , 'create_date': ticket.create_date
                              , 'fulfill': ticket.data.get('fulfill')
                              , 'note': render_to_string('order/pinnacle_note.html',
                                        {'text': ticket.data.get('reviewSummary')
                                        ,'description': 'Review Summary'})
                              })
        return ticket_list

    def get_owner_instance(self, name):

        mc = get_mc_group(name)

        if mc:
            dn = mc.entry_dn[3:mc.entry_dn.find(',')]

            try:
                so = StorageOwner.objects.get(name=dn)
            except: #Make it so
                so = StorageOwner()
                so.name = dn
                so.save()

                for member in mc['member']:
                    uid = member[4:member.find(',')]
                    sm = StorageMember()
                    sm.storage_owner = so
                    sm.username = uid
                    sm.save()

            return so

    class Meta:
        abstract = True 


class VolumeHost(models.Model):
    #storage_instance = models.ForeignKey(StorageInstance, related_name='hosts', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True 


class StorageInstance(Volume):
    owner_bak = models.ForeignKey(StorageOwner, on_delete=models.CASCADE, null=True, blank=True)
    owner_name = models.CharField(max_length=100, null=True, blank=True) # TODO Remove
    deptid = models.CharField(max_length=6, null=True, blank=True)
    autogrow = models.BooleanField(default=False)
    flux = models.BooleanField(default=False)

    def get_shortcodes(self):
        return [{"shortcode": self.shortcode, "size": self.size}]

    def get_hosts(self):
        return StorageHost.objects.filter(storage_instance=self)

    def update_hosts(self, host_list):
        current_set = set(StorageHost.objects.filter(storage_instance=self).values_list('name', flat=True) )
        new_set = set(host_list)
        
        for host in current_set.difference(new_set):
            host = StorageHost.objects.get(storage_instance=self, name=host)
            host.delete()

        for host in new_set.difference(current_set):
            if host != '':
                ah = StorageHost()
                ah.storage_instance = self
                ah.name = host
                ah.save()

class StorageHost(VolumeHost):
    storage_instance = models.ForeignKey(StorageInstance, related_name='hosts', on_delete=models.CASCADE)


class ArcInstance(Volume):

    nfs_group_id = models.CharField(max_length=100, blank=True, null=True)
    multi_protocol = models.BooleanField(default=False)  
    sensitive_regulated = models.BooleanField(default=False)  
    great_lakes = models.BooleanField(default=False) 
    armis = models.BooleanField(default=False) 
    lighthouse = models.BooleanField(default=False) 
    globus = models.BooleanField(default=False) 
    globus_phi = models.BooleanField(default=False) 
    thunder_x = models.BooleanField(default=False)
    research_computing_package = models.BooleanField(default=False)
    amount_used = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)

    class meta:
        verbose_name = 'ARC Storage Instance'   
        verbose_name_plural = 'ARC Storage Instances'

    def get_hosts(self):
        return ArcHost.objects.filter(arc_instance=self)

    def get_shortcodes(self):
        return ArcBilling.objects.filter(storage_instance=self)

    def update_hosts(self, host_list):
        current_set = set(ArcHost.objects.filter(arc_instance=self).values_list('name', flat=True) )
        new_set = set(host_list)
        
        for host in current_set.difference(new_set):
            host = ArcHost.objects.get(arc_instance=self, name=host)
            host.delete()

        for host in new_set.difference(current_set):
            if host != '':
                ah = ArcHost()
                ah.arc_instance = self
                ah.name = host.strip()
                ah.save()
            
    def get_shortcodes(self):
        return ArcBilling.objects.filter(arc_instance=self)


class ArcHost(VolumeHost):
    arc_instance = models.ForeignKey(ArcInstance, related_name='hosts', on_delete=models.CASCADE)

    class meta:
        verbose_name = 'Host'   


class ArcBilling(models.Model):
    arc_instance = models.ForeignKey(ArcInstance, related_name='shortcodes', on_delete=models.CASCADE)
    size = models.IntegerField()
    shortcode = models.CharField(max_length=100)

    def __str__(self):
        return self.shortcode

class BackupDomain(models.Model):
    RATE_NAME = 'MB-MCOMM'

    name = models.CharField(max_length=100)
    owner = models.ForeignKey(LDAPGroup, on_delete=models.CASCADE)
    shortcode = models.CharField(max_length=100)
    size = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_calculated_date = models.DateTimeField(null=True)
    versions_while_exists = models.PositiveIntegerField()
    versions_after_deleted = models.PositiveIntegerField()
    days_extra_versions = models.PositiveIntegerField()
    days_only_version = models.PositiveIntegerField()

    #def save(self, *args, **kwargs):
    #    if self.orig_cost != self.total_cost:
    #        self.cost_calculated_date = datetime.now()
    #    super(BackupDomain, self).save(*args, **kwargs)

    @property
    def total_cost(self):
        rate = StorageRate.objects.get(name=self.RATE_NAME)
        total_cost = round(rate.rate * self.size, 2)
        return total_cost

    def __init__(self, *args, **kwargs):
        super(BackupDomain, self).__init__(*args, **kwargs)
        self.orig_cost = self.total_cost

    def __str__(self):
        return self.name
    
    def get_checkboxes(self):
        return []

    def get_user_subscriptions(self, username):
        groups = list(LDAPGroupMember.objects.filter(username=username).values_list('ldap_group_id'))
        return BackupDomain.objects.filter(owner__in=groups).order_by('name')


class BackupNode(models.Model):
    backup_domain = models.ForeignKey(BackupDomain, related_name='nodes', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    time = models.CharField(max_length=8)

    def __str__(self):
        return self.name


class DayOfWeek(models.IntegerChoices):
    SUNDAY = 0, 'Sunday'
    MONDAY = 1, 'Monday'
    TUESDAY = 2, 'Tuesday'
    WEDNESDAY = 3, 'Wednesday'
    THURSDAY = 4, 'Thursday'
    FRIDAY = 5, 'Friday'
    SATURDAY = 6, 'Saturday'


class Server(models.Model):
    BUSINESS_HOURS = 0
    ALL_HOURS = 1

    ON_CALL_CHOICES = [
        (BUSINESS_HOURS, 'Business Hours'),
        (ALL_HOURS, '24/7'),
    ]

    MANAGED_FIELDS = ['patch_time', 'patch_day', 'reboot_time', 'reboot_day']

    for rate in StorageRate.objects.filter(name__startswith='SV-'):
        if rate.name == 'SV-RAM':
            ram_rate = rate.rate
        elif rate.name == 'SV-DI-REP':
            disk_replicated = rate.rate
        elif rate.name == 'SV-DI-NONREP':
            disk_no_replication = rate.rate
        elif rate.name == 'SV-DI-BACKUP':
            disk_backup = rate.rate

    name = models.CharField(max_length=100)  #  <name>PS-VD-DIRECTORY-1</name>
    owner = models.ForeignKey(LDAPGroup, on_delete=models.CASCADE, null=True)  #<mcommGroup>DPSS Technology Management</mcommGroup>
    admin_group = models.ForeignKey(LDAPGroup, on_delete=models.CASCADE, null=True, related_name='admin_group')
    database_type = models.ForeignKey(Choice, null=True, blank=True, limit_choices_to={"parent__code": "DATABASE_TYPE"}, on_delete=models.SET_NULL, related_name='database_type')
    shortcode = ShortCodeField()
    created_date = models.DateTimeField(default=timezone.now, null=True)
    #shortcode = models.CharField(max_length=100) 
    public_facing = models.BooleanField(default=False)
    managed = models.BooleanField(default=True)   #  <SRVmanaged></SRVmanaged>

    os = models.ForeignKey(Choice, null=True, blank=True, limit_choices_to={'parent__code__in': ['SERVER_UNMANAGED_OS','LINUX','WINDOWS']}
                                    , related_name='os'
                                    , on_delete=models.CASCADE,)

    cpu = models.IntegerField('CPU')   #  <cpu>4</cpu>
    ram = models.IntegerField('RAM')    #  <ram>8</ram>
    regulated_data = models.ManyToManyField(Choice, blank=True, limit_choices_to={"parent__code": "REGULATED_SENSITIVE_DATA"}, related_name='regulated')
    non_regulated_data = models.ManyToManyField(Choice, blank=True, limit_choices_to={"parent__code": "NON_REGULATED_SENSITIVE_DATA"})
    replicated = models.BooleanField(default=True)

    on_call = models.PositiveSmallIntegerField(null=True, choices=ON_CALL_CHOICES)   #<monitoringsystem>businesshours</monitoringsystem>
    in_service = models.BooleanField(default=True)   #<servicestatus>Ended</servicestatus>

    firewall = models.CharField(max_length=100)
    backup = models.BooleanField(default=False)
    support_email = models.CharField(max_length=100)    #  <afterhoursemail>dpss-technology-management@umich.edu</afterhoursemail>
    support_phone = models.CharField(max_length=100)   #  <afterhoursphone>7346470657</afterhoursphone>
    backup_time = models.ForeignKey(Choice, null=True, blank=True, limit_choices_to={"parent__code": "SERVER_BACKUP_TIME"}
                                    , related_name='backup_time'
                                    , on_delete=models.CASCADE,)
    patch_time = models.ForeignKey(Choice, null=True, blank=True, limit_choices_to={"parent__code": "SERVER_PATCH_TIME"}
                                    , related_name='patch_time'
                                    , on_delete=models.CASCADE,)
    patch_day = models.ForeignKey(Choice, null=True, blank=True, limit_choices_to={"parent__code": "SERVER_PATCH_DATE"}
                                    , related_name='patch_day'
                                    , on_delete=models.CASCADE,)
    reboot_time = models.ForeignKey(Choice, null=True, blank=True, limit_choices_to={"parent__code": "SERVER_REBOOT_TIME"}
                                    , related_name='reboot_time'
                                    , on_delete=models.CASCADE,)

    reboot_day = models.ForeignKey(Choice, null=True, blank=True, limit_choices_to={"parent__code": "SERVER_REBOOT_DATE"}
                                    , related_name='reboot_day'
                                    , on_delete=models.CASCADE,)
    domain = models.CharField(max_length=100)
    datacenter = models.CharField(max_length=100)
    firewall_requests = models.CharField(max_length=100)
    legacy_data = models.TextField()

    @cached_property
    def total_disk_size(self):
        disk = ServerDisk.objects.filter(server=self).aggregate(models.Sum('size'))
        if disk:
            sum = disk['size__sum']
            if sum:
                return disk['size__sum']

        return 0

    @property
    def ram_cost(self):
        return self.ram * self.ram_rate

    @property
    def backup_cost(self):
        if self.backup:
            return self.total_disk_size * self.disk_backup
        else:
            return 0

    @property
    def disk_cost(self):
        if self.total_disk_size:
            if self.replicated:
                return self.total_disk_size * self.disk_replicated
            else:
                return self.total_disk_size * self.disk_no_replication
        else:
            return 0

    @property
    def total_cost(self):
        return self.ram_cost + self.backup_cost + self.disk_cost

    def __str__(self):
        return self.name

    def get_shortcodes(self):
        return [{'size':'', 'shortcode':self.shortcode}]

    def get_checkboxes(self):
        return [] 


class ServerDisk(models.Model):
    CONTROLLER_LIST = [(0,0),(1,1),(2,2),(3,3),]
    DEVICE_LIST = []
    for i in range(0,16):
        if i != 7:  # VMWare hates 7's
            DEVICE_LIST.append((i,i))

    server = models.ForeignKey(Server, related_name='disks', on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    controller = models.IntegerField(choices=CONTROLLER_LIST)
    device = models.IntegerField(choices=DEVICE_LIST)
    size = models.IntegerField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if self.controller == None or self.device == None:
            self.set_scsi_id()

        super().save(*args, **kwargs)  # Call the "real" save() method.


    def set_scsi_id(self):   # Set controller/device defaults based on name
        num = int(self.name[4:])

        controller = 0
        device = 0

        for i in range(0, num):
            device += 1
            if device == 7:
                device = 8
            elif device == 16:
                device = 0
                controller += 1

        self.controller = controller
        self.device = device

        return 


def get_disk_size(server):
    size = ServerDisk.objects.filter(server=server)
    print(size)

class ServerData(models.Model):
    server = models.ForeignKey(Server, related_name='data', on_delete=models.CASCADE)
    code = models.CharField(max_length=5)


class Database(models.Model):
    MDB_ADMIN_GROUP = 1110

    MYSQL = 0
    MSSQL = 1
    ORACLE = 2

    TYPE_CHOICES = [
        (MYSQL, 'MYSQL'),
        (MSSQL, 'MSSQL'),
        (ORACLE, 'Oracle'),
    ]

    BUSINESS_HOURS = 0
    ALL_HOURS = 1

    ON_CALL_CHOICES = [
        (BUSINESS_HOURS, 'Business Hours'),
        (ALL_HOURS, '24/7'),
    ]

    name = models.CharField(max_length=100)  #  <name>PS-VD-DIRECTORY-1</name>
    in_service = models.BooleanField(default=True)   #<servicestatus>Ended</servicestatus>
    owner = models.ForeignKey(LDAPGroup, on_delete=models.CASCADE, null=True)  #<mcommGroup>DPSS Technology Management</mcommGroup>
    shortcode = models.CharField(max_length=100) 
    created_date = models.DateTimeField(default=timezone.now)
    size = models.IntegerField(null=True)
    type = models.ForeignKey(Choice, null=True, blank=True, limit_choices_to={"parent__code": "DATABASE_TYPE"}, on_delete=models.SET_NULL, related_name='type')
    #version = models.ForeignKey(Choice, null=True, blank=True, limit_choices_to={"parent__code": "DATABASE_VERSION"}, on_delete=models.SET_NULL, related_name='version')
    purpose = models.TextField()
    on_call = models.PositiveSmallIntegerField(null=True, choices=ON_CALL_CHOICES)
    url = models.URLField(null=True, blank=True)
    support_email = models.CharField(max_length=100)    #  <afterhoursemail>dpss-technology-management@umich.edu</afterhoursemail>
    support_phone = models.CharField(max_length=100)   #  <afterhoursphone>7346470657</afterhoursphone>
    server = models.ForeignKey(Server, null=True, blank=True, on_delete=models.SET_NULL)
    legacy_data = models.TextField()


    def __str__(self):
        return self.name

    @property
    def total_cost(self):
        if self.server:
            return self.server.total_cost
        else:
            return 0

    @property
    def shared(self):
        if self.server:
            return False
        else:
            return True

    def get_shortcodes(self):
        return [{'size':'', 'shortcode':self.shortcode}]
        
    def get_checkboxes(self):
        return []


class Order(models.Model):
    PRIORITY_CHOICES = (
        ('High', 'Expedited'),
        ('Medium', 'Standard'),
        ('Low', 'Low'),
    )

    order_reference = models.CharField(max_length=20)
    create_date = models.DateTimeField('Date Created', auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    chartcom = models.ForeignKey(Chartcom, on_delete=models.CASCADE)
    #status = models.CharField(max_length=20)
    priority = models.CharField(max_length=20, default='Medium', choices=PRIORITY_CHOICES)
    due_date = models.DateTimeField(blank=True, null=True)

    @property
    def dept(self):
        return self.chartcom.dept

    @property
    def status(self):
        srs_status = 'N/A'

        if self.order_reference == 'TBD':
            srs_status = 'Submitted'
        else:
            try:
                pin = UmOscPreorderApiV.objects.get(add_info_text_3=str(self.id),pre_order_issue=1)
                srs_status = pin.work_status_name
                if(pin.work_status_name == "Received"):
                    srs_status = "Submitted"
                if pin.status_code == 2:
                    if(pin.work_status_name == "Cancelled"):
                        srs_status = "Cancelled"
                    else:
                        srs_status = "Completed"
            except:
                print('error')

        return srs_status

    def add_contact(self):

        u = get_mc_user(self.created_by.username)
        uniqname = str(u['uid'])
        first_name = str(u['givenName'])
        middle_name = ''
        last_name = str(u['umichDisplaySn'])
        primary_email = str(u['mail'])
        primary_phone = str(u['telephoneNumber'])
        dept = self.chartcom.dept

        with connections['pinnacle'].cursor() as cursor:
            cursor.callproc('pinn_custom.um_osc_util_k.um_add_new_contact_p', [uniqname, first_name, middle_name, last_name, primary_email, primary_phone, dept])

    def add_attachments(self):

        item_list = Item.objects.filter(order=self)

        for num, item in enumerate(item_list, start=2):
            attachment_list = Attachment.objects.filter(item_id=item.id)

            if len(attachment_list) > 0:
                pre_order_id = UmOscPreorderApiV.objects.get(add_info_text_3=self.id, add_info_text_4=item.id).pre_order_id

                #with connections['pinnacle'].cursor() as cursor:
                #    cursor.callproc('pinn_custom.um_note_procedures_k.um_create_note_p', ['Work Order', None, pre_order_id, 'files', 'attachments', None, self.created_by.username] )

                with connections['pinnacle'].cursor() as cursor:
                    noteid = cursor.callfunc('pinn_custom.um_note_procedures_k.um_get_note_id_f', cx_Oracle.STRING , ['Work Order', pre_order_id, 'Order Detail'] )
                    id = int(noteid)

                for attachment in attachment_list:
                    filename = attachment.file.name[12:99]
                    fileData = attachment.file.read()

                    conn = connections['pinnacle'].connection
                    lob = conn.createlob(cx_Oracle.BLOB)  
                    lob.write(fileData)

                    with connections['pinnacle'].cursor() as cursor:
                        noteid = cursor.callproc('pinn_custom.um_note_procedures_k.um_make_blob_an_attachment_p',  ['Note', id,'files', filename, lob] )


    def create_preorder(self):

        self.add_contact()

        data =  {  
                    "department_number": self.chartcom.dept,
                    "default_one_time_expense_acct": self.chartcom.account_number,
                    "submitter": self.created_by.username,
                    "add_info_text_3": self.id,
                }

        if self.due_date:
            if type(self.due_date) == str:   # If resubmitting this is in date format
                data['due_date'] = self.due_date
            else:
                data['due_date'] = self.due_date.strftime('%Y-%m-%d')

        item_list = Item.objects.filter(order_id=self.id)
        elements = Element.objects.exclude(target__isnull=True).exclude(target__exact='')
        map = {}

        for element in elements:
            map[element.name] = element.target

        equipment_only = True
        wiring_only = True
        create_bill_only = False   #set to true when it hits a category 0 type is not equipment or wiring  

        for num, item in enumerate(item_list, start=1):
            issue = {}
            if num == 1:
                data['priority_name'] = self.priority
                data['issues'] = []

            action_id = item.data['action_id']
            action = Action.objects.get(id=action_id)

            cons = Constant.objects.filter(action=action_id)
            for con in cons:  # Populate issue with constants
                issue[con.field] = con.value

            if action.type != 'E':
                equipment_only = False

            if action_id != '41':
                wiring_only = False

            if issue['wo_type_category_id'] == '0':
                if action_id != '37' and action_id != '41':
                    create_bill_only = True

            for key, value in item.data.items():
                if value:  # Populate issue with user supplied values
                    if key == 'MRC' or key == 'localCharges' or key == 'LD':
                        value = Chartcom.objects.get(id=value).account_number

                    target = map.get(key)
                    if target != None:
                        issue[target] = value

            issue['add_info_text_4'] = item.id
            issue['note'] = item.format_note()
            issue['comment_text'] = item.description
            data['issues'].append(issue)

        if equipment_only:
            data['equipment_only'] = 'Y'
    
        if wiring_only:
            data['wiring_only'] = 'Y'
    
        if create_bill_only:
            data['create_bill_only'] = 'Y'
        else:
            data['create_bill_only'] = 'N'

        json_data = json.dumps({"Order": data})

        LogItem().add_log_entry('JSON', self.id, json_data)

        cursor = connections['pinnacle'].cursor()

        try: 
            cursor.callproc("dbms_output.enable")
            ponum = cursor.callfunc('um_osc_util_k.um_add_preorder_f', cx_Oracle.STRING , [json_data])

            self.order_reference = ponum
            self.save()
            
            self.add_attachments()

        except cx_Oracle.DatabaseError as e:
            LogItem().add_log_entry('Error', self.id, e)
            num = str(self.id)
            url = settings.SITE_URL + '/orders/integration/'  + num
            send_mail('SRS Order # ' + num + ' failed to submit', url, 'itscomm.information.systems@umich.edu', ['itscomm.information.systems@umich.edu'])

        finally:
            dbms_output = ''

            while True:
                out = cursor.callproc("dbms_output.get_line", ('',0)) 
                if out[1] > 0:
                    break
                
                dbms_output = dbms_output + out[0] + '\n'
            
            LogItem().add_log_entry('DBMS_OUTPUT', self.id, dbms_output)
            cursor.close()

class Item(models.Model):
    description = models.CharField(max_length=100)
    create_date = models.DateTimeField('Date Created', auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    deptid = models.CharField(max_length=8)
    chartcom = models.ForeignKey(Chartcom, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    data = models.JSONField()
    external_reference_id = models.PositiveIntegerField(null=True)
    internal_reference_id = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.description

    @property
    def days_to_deletion(self):
        delete_date = self.create_date + timedelta(days=180) 
        days_to_deletion = delete_date - timezone.now()
        return days_to_deletion.days

    def format_note(self):
        text = self.data['reviewSummary']

        if isinstance(text, str):  #TODO Legacy orders
            text = literal_eval(text)
            note = render_to_string('order/pinnacle_note.html', {'text': text, 'description': self.description})
        else:
            note = render_to_string('order/pinnacle_note.html', {'text': text, 'description': self.description})

        return note

    def route(self):
        action = Action.objects.get(id=self.data['action_id'])
        routing = action.service.routing

        if action.use_cart:  # Associate with blank order
            o = Order()
            o.order_reference = action.destination
            o.chartcom = self.chartcom
            o.service = action.service
            o.created_by = self.created_by
            o.save()
            self.order = o
            self.save()

        for route in routing['routes']:
            if route['target'] == 'tdx':
                self.submit_incident(route, action) 

            if route['target'] == 'database':
                if 'fulfill' in route:
                    if route['fulfill'] == 'manual' and action.type != 'A':
                        self.data['fulfill'] = 'Pending'
                        self.save()
                        continue

                self.update_database(route)

    def update_database(self, route):
        action = Action.objects.get(id=self.data['action_id'])

        if action.type == 'A':  # For Adds instantiate a new record
            rec = globals()[route['record']]()
            rec.created_date = datetime.now()
        else: # upddate/delete get existing record
            rec = globals()[route['record']].objects.get(id=self.data.get('instance_id'))
        
        if self.data.get('volaction') == 'Delete':
            if action.service.id == 14:  # MiDatabase
                rec.in_service = False
                rec.save()
            else:
                rec.delete()
        else:
            if action.service.id == 8:
                self.update_mibackup(rec)
            elif action.service.id == 13:
                self.update_server(rec)
            elif action.service.id == 14:
                self.update_db(rec)
            else:
                rec.owner = LDAPGroup().lookup( self.data['owner'] )
                rec.service = action.service
                rec.name = self.data.get('name','').strip()
                rec.owner = LDAPGroup().lookup( self.data['owner'] )
                rec.size = self.data.get('size',0)
                rec.service = action.service

                print('rate for ', action.service.id)
                if action.service.id == 11:
                    rec.rate_id = 28
                    print(rec.rate_id, 'set for dd')
                else:
                    rec.rate_id = self.data.get('selectOptionType')
                
                if action.service.name in ['turboResearch','dataDen']:
                    if self.data.get('research_comp_pkg') == 'yes':
                        rec.research_computing_package = True
                    else:
                        rec.research_computing_package = False

                rec.type = action.override['storage_type']
                rec.shortcode = self.data.get('shortcode')
                rec.uid = self.data.get('uid')
                rec.ad_group = self.data.get('ad_group').strip()
                if action.service.id == 7:
                    self.update_mistorage(rec)
                else:
                    self.update_arcts(rec)
                                    
                rec.save()

                if self.data.get('permittedHosts'):
                    rec.update_hosts(self.data.get('permittedHosts'))

    def submit_incident(self, route, action):

        text = self.data['reviewSummary']
        note = render_to_string('order/pinnacle_note.html', {'text': text, 'description': self.description})
 
        payload = route['constants']
        payload['Title'] = self.description
        payload['RequestorEmail'] = self.created_by.email
        payload['Description'] = f'{note}\n'

        # Add Attributes using target mapping
        field_map = action.override.get('map', '')

        display_values = {}
        for tab in self.data['reviewSummary']:
            for field in tab['fields']:
                if 'name' in field:
                    if 'list' in field:
                        nl = '\n'
                        display_values[field['name']] = nl.join(field['list'])
                    else:
                        display_values[field['name']] = field['value']

        attributes = []
        step_list = Step.objects.filter(action=action)
        element_list = Element.objects.filter(step__in=step_list, target__isnull=False)
        for element in element_list:
            value = display_values.get(element.name)
            if value:
                if element.name in field_map:
                    attributes.append({'ID': field_map[element.name], 'Value': value})
                else:
                    attributes.append({'ID': element.target, 'Value': value})

        dedicated = False
        if action.service.name == 'midatabase':
            if self.data.get('volaction') == 'Delete':
                payload['Title'] = 'Delete MiDatabase'
                instance_id = self.data.get('instance_id')
                db_type = Database.objects.get(id=instance_id).type.label
                attributes.append({'ID': 1858, 'Value': db_type})

        elif action.service.name == 'miServer':
            attributes.append({'ID': 1954, 'Value': self.data.get('shortcode')})

            if self.data.get('michmed_flag') == 'Yes':
                michmed = 21619  # Yes
            else:
                michmed = 21618  # No

            attributes.append({'ID': 8480, 'Value': michmed})

            if action.type == 'M':
                instance_id = self.data.get('instance_id')
                instance = Server.objects.get(id=instance_id)
                if instance.managed:
                    mod_man = 'True'
                    if instance.admin_group.name == 'MiDatabase Support Team':
                        dedicated = True
                else:
                    mod_man = 'False'
                os_id = instance.os_id
                if self.data.get('volaction') == 'Delete':
                    attributes.append({'ID': 1959, 'Value': instance.name})
                    attributes.append({'ID': 1951, 'Value': 202})
                    payload['Title'] = f'Delete MiServer {instance.name}'
                else:
                    attributes.append({'ID': 1959, 'Value': instance.name})
                    attributes.append({'ID': 1951, 'Value': 201})
                    payload['Title'] = f'Modify MiServer {instance.name}'
            else:
                payload['Title'] = 'New MiServer Request'
                mod_man = None
                os_id = None
                if self.data.get('public_facing') == 'True':
                    attributes.append({'ID': 1967, 'Value': 'public'})
                else:
                    attributes.append({'ID': 1967, 'Value': 'secure'})

            db = self.data.get('database')
            if db:
                attributes.append({'ID': 1874, 'Value': 93}) # Dedicated DB

                if self.data.get('volaction') == 'Delete':
                    payload['Title'] = 'Delete MiDatabase'  # TODO Unreachable?
                else:
                    group_name = self.data.get('ad_group')
                    attributes.append({'ID': 1953, 'Value': MCommunity().get_group_email_and_name(group_name)})  # Admin Group

                attributes.append({'ID': 5319, 'Value': db})
                attributes.append({'ID': 1858, 'Value': db})
                attributes.append({'ID': 1952, 'Value': 203}) # Managed

                if db == 'MSSQL':
                    attributes.append({'ID': 1994, 'Value': 215}) # Windows
                    os = Choice.objects.get(code='Windows2022managed')
                else:
                    attributes.append({'ID': 1994, 'Value': 216}) # Linux
                    os = Choice.objects.get(code='RedHatEnterpriseLinux8')
                    
                attributes.append({'ID': 1957, 'Value': os.label}) 
            else:
                if self.data.get('volaction') == 'Delete':
                    payload['Title'] = 'Delete MiServer'
                else:
                    if dedicated: # modifying a dedicated DB server
                        group_name = instance.admin_group.name
                        attributes.append({'ID': 5319, 'Value': instance.database_type.code})
                    else:
                        group_name = self.data.get('owner')
                        
                    attributes.append({'ID': 1953, 'Value': MCommunity().get_group_email_and_name(group_name)})  # Admin Group

                managed = self.data.get('managed', mod_man)
                if managed == 'True' or db:
                    os = Choice.objects.get(id=self.data.get('misevos', os_id))
                    attributes.append({'ID': 1952, 'Value': 203}) # Managed
                    if os.code.startswith('Windows'):
                        attributes.append({'ID': 1994, 'Value': 215}) # Windows
                    else:
                        attributes.append({'ID': 1994, 'Value': 216}) # Linux
                else:
                    os = Choice.objects.get(id=self.data.get('misernonmang', os_id))
                    attributes.append({'ID': 1952, 'Value': 207}) # Non-Managed
                    attributes.append({'ID': 1994, 'Value': 214}) # IAAS
                
                attributes.append({'ID': 1957, 'Value': os.label}) 

            if self.data.get('volaction') != 'Delete':
                if action.type == 'M':
                    summ = text[2]['fields']
                else:
                    summ = text[1]['fields']

                for field in summ:
                    if field['label'] == 'Disk Space':
                        nl = '\n'
                        disks = nl.join(field['list'])
                        attributes.append({'ID': 1965, 'Value': disks})

        # Add Action Constants to Payload
        cons = Constant.objects.filter(action=action)

        for con in cons:  # Add Action Constants
            attributes.append({'ID': con.field, 'Value': con.value})

        for attr in attributes:
            if type(attr['ID']) == int:
                attr['ID'] = str(attr['ID'])
            if type(attr['Value']) == int:
                attr['Value'] = str(attr['Value'])

        payload['Attributes'] = attributes

        response = TDx().create_ticket(payload=payload)
 
        self.external_reference_id = json.loads(response.text)['ID']
        self.save()   # Save incident number to item

    def update_db(self, rec):
        rec.owner = LDAPGroup().lookup( self.data['owner'] )

        for field in ['purpose','size','name','support_email','support_phone','shortcode','type','url']:
            value = self.data.get(field)
            if value:
                setattr(rec, field, value)

        on_call = self.data.get('on_call', '0')
        rec.on_call = int(on_call)

        type = self.data.get('midatatype')
        if type:
            rec.type = Choice.objects.get(id=type)
            
        rec.save()

    def update_server(self, rec):
        rec.owner = LDAPGroup().lookup( self.data['owner'] )

        if self.data.get('ad_group'):
            rec.admin_group = LDAPGroup().lookup( self.data['ad_group'] )
        else:
            if not rec.admin_group:
                rec.admin_group = rec.owner                
            elif rec.admin_group.name != 'MiDatabase Support Team':
                rec.admin_group = rec.owner

        MCommunity().add_entitlement(rec.admin_group.name)

        for field in ['cpu','ram','name','support_email','support_phone','shortcode','backup','managed','replicated','public_facing']:
            value = self.data.get(field)
            if value:
                setattr(rec, field, value)

        on_call = self.data.get('on_call', '0')
        rec.on_call = int(on_call)

        for field in ['backup_time','patch_day','patch_time','reboot_day','reboot_time']:
            value = self.data.get(field)
            if value:
                value = int(value)
                setattr(rec, field + '_id', value)

        if rec.managed == 'True' or rec.managed == True:
            os = self.data.get('misevos')
        else:
            os = self.data.get('misernonmang')

        if os:
            rec.os = Choice.objects.get(id=os)
        elif self.data.get('database'):
            rec.on_call = 1   # Server is on call even if DB is not
            if self.data.get('database') == 'MSSQL':
                rec.os = Choice.objects.get(code='Windows2022managed')
                rec.backup = True
                rec.backup_time_id = 13  # 6:00 PM
                rec.patch_day_id = 98    # Saturday
                rec.patch_time_id = 40   # 5:00 AM
            else:
                rec.os = Choice.objects.get(code='RedHatEnterpriseLinux8')

        db_type = self.data.get('database')
        if db_type:
            rec.database_type = Choice.objects.get(parent__code='DATABASE_TYPE', label=db_type)
        
        rec.save()

        d = self.data.get('non_regulated_data')
        if d:
            print(d)
            if type(d) == str:
                d = [d]
            rec.non_regulated_data.set(d)

        d = self.data.get('regulated_data')
        if d:
            if type(d) == str:
                d = [d]
            rec.regulated_data.set(d)

        rec.save()

        for disk in range(0, int(self.data.get('form-TOTAL_FORMS'))):            
            size = self.data.get('form-'+str(disk)+'-size')
            uom = self.data.get('form-'+str(disk)+'-uom')
            name = self.data.get('form-'+str(disk)+'-name')

            if uom == 'TB':
                size = int(size) * 1024

            d = ServerDisk.objects.update_or_create(server=rec,name=name,
                defaults={'size': size})

    def update_mibackup(self, rec):
        if rec.name == '':
            rec.name = 'temp'

        rec.owner = LDAPGroup().lookup( self.data['mCommunityName'] )
        rec.shortcode = self.data['shortcode']
        #rec.size = 0
        rec.versions_while_exists = self.data['versions_while_exist']
        rec.versions_after_deleted = self.data['versions_after_delet']
        rec.days_extra_versions = self.data['days_extra_versions']
        rec.days_only_version = self.data['days_only_version']
        rec.save()

        time_list = self.data['backupTime']
        ampm_list=self.data['backupTimeampm']

        for num, node in enumerate(self.data['nodeNames']):
            if node != '':
                time = time_list[num]+' '+ampm_list[num]
                new_node = BackupNode.objects.get_or_create(backup_domain=rec, name=node, defaults={'time': time})
                new_time = new_node[0].time
                if new_time != time:
                    new_node[0].time = time
                    new_node[0].save()

        ex = BackupNode.objects.filter(backup_domain=rec).exclude(name__in=self.data['nodeNames']).delete()

    def update_arcts(self, rec):

        rec.nfs_group_id = self.data.get('nfs_group_id').strip()

        if self.data.get('sensitive_regulated') == 'yessen':
            rec.sensitive_regulated = True
        else:
            rec.sensitive_regulated = False

        if self.data.get('multi_protocol') == 'ycifs':
            rec.multi_protocol = True
        else:
            rec.multi_protocol = False
        
        rec.armis = False
        rec.globus_phi = False
        rec.lighthouse = False
        rec.globus = False
        rec.thunder_x = False
        rec.great_lakes = False

        if self.data.get('hipaaOptions'):
            if 'armis' in self.data.get('hipaaOptions'):
                rec.armis = True
            if 'globus_phi' in self.data.get('hipaaOptions'):
                rec.globus_phi = True


        if self.data.get('nonHipaaOptions'):
            if 'lighthouse' in self.data.get('nonHipaaOptions'):
                rec.lighthouse = True

            if 'globus' in self.data.get('nonHipaaOptions'):
                rec.globus = True

            if 'thunder_x' in self.data.get('nonHipaaOptions'):
                rec.thunder_x = True

            if 'great_lakes' in self.data.get('nonHipaaOptions'):
                rec.great_lakes = True

        #if self.data.get('great_lakes') == 'yes':
        #    rec.great_lakes = True
        #else:
        #    rec.great_lakes = False

        rec.save()
        self.internal_reference_id = rec.id
        self.save() # Save the instance ID on the item 
        bill_size_list = self.data.get('terabytes')

        ArcBilling.objects.filter(arc_instance=rec).delete()

        for num, shortcode in enumerate(self.data.get('shortcode')):
            if shortcode:
                sc = ArcBilling()
                sc.arc_instance = rec
                sc.size = bill_size_list[num]
                sc.shortcode = shortcode
                sc.save()

    def update_mistorage(self, rec):

        if self.data.get('flux') == 'yes':
            rec.flux = True

    def leppard(self):
        pour=['me']
        pour.append('sugar')

class Attachment(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments',blank=True, null=True)


class Ticket(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    instance = models.ForeignKey(ArcInstance, null=True, on_delete=models.DO_NOTHING)
    ticket_id = models.PositiveIntegerField()
    status = models.CharField(max_length=10)
    data = models.JSONField()

    @property
    def ticket_link(self):
        return f'{TDX_URL}{self.ticket_id}'

    class Meta:
        db_table = 'order_item_ticket_v'
        managed = False

    def __str__(self):
        return str(self.ticket_id)
