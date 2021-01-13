from django.conf import settings
from django.core.mail import send_mail
from django.contrib.postgres.fields import JSONField
from django.contrib.admin.models import LogEntry, ADDITION
from django.db import models
from oscauth.models import Role, LDAPGroup, LDAPGroupMember
from project.pinnmodels import UmOscPreorderApiV
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.db import connections
from django.template.loader import render_to_string
from ast import literal_eval
import json, io, os, requests
import cx_Oracle
from oscauth.utils import get_mc_user, get_mc_group

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
        ('DataDenForm', 'Data Den Form')
    )

    custom_form = models.CharField(blank=True, max_length=20, choices=FORM_CHOICES)
    progressive_disclosure = models.BooleanField(default=False)

class Element(Configuration):
    ELEMENT_CHOICES = (
        ('', ''),
        ('Radio', 'Radio'),
        ('ST', 'String'),
        ('List', 'List'),
        ('NU', 'Number'),
        ('Chart', 'Chartcom'),
        ('Label', 'Label'),
        ('Checkbox', 'Checkbox'),
        ('McGroup', 'MCommunity Group'),
        ('ShortCode', 'Short Code'),
        ('Phone', 'Phone Number'),
        ('Uniqname', 'Uniqname'),
        ('HTML', 'Static HTML'),
    )
    label = models.TextField()
    description = models.TextField(blank=True)
    help_text = models.TextField(blank=True)
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=ELEMENT_CHOICES)
    attributes = models.CharField(blank=True, max_length=1000)
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
    routing = JSONField(default=dict)


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
    override = JSONField(null=True, blank=True)
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
        dept_list = UserChartcomV.objects.filter(user=self).order_by('dept').distinct('dept')
        user_chartcom_depts = []
        
        for chartcom in dept_list:
            user_chartcom_depts.append((chartcom.dept))

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
        db_table = 'order_user_chartcom'


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

        cur = connections['default'].cursor()
        cur.execute("select external_reference_id, create_date, data from order_item "
                    "where cast(data->>'action_id' as INTEGER) in (select id from order_action where service_id = %s) "
                    "  and cast(data->>'instance_id' as INTEGER) = %s "
                    "  and external_reference_id is not null "
                    "order by create_date desc"
                    ,[self.service_id, self.id])

        if settings.ENVIRONMENT == 'Production':
            tdx_url = 'https://teamdynamix.umich.edu/TDNext/Apps/31/Tickets/TicketDet.aspx?TicketID='
        else:
            tdx_url = 'https://teamdynamix.umich.edu/SBTDNext/Apps/31/Tickets/TicketDet?TicketID='

        ticket_list = []
        for row in cur.fetchall():

            fulfill = ''

            try:
                data = json.loads(row[2])
                note = render_to_string('order/pinnacle_note.html', {'text': data['reviewSummary'], 'description': 'Review Summary'})
                if 'fulfill' in data:
                    fulfill = data['fulfill']
            except:
                note = ''


            ticket_list.append({'id': row[0]
                              , 'url': f'{tdx_url}{row[0]}'
                              , 'create_date': row[1]
                              , 'fulfill': fulfill
                              , 'note': note})

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
                ah.name = host
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


class Server(models.Model):

    ON_CALL_CHOICES = [
        (0, 'Business Hours'),
        (1, '24/7'),
    ]

    DAY_CHOICES = [
        (0, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    ]

    name = models.CharField(max_length=100)  #  <name>PS-VD-DIRECTORY-1</name>
    owner = models.ForeignKey(LDAPGroup, on_delete=models.CASCADE, null=True)  #<mcommGroup>DPSS Technology Management</mcommGroup>
    shortcode = models.CharField(max_length=100) 
    managed = models.BooleanField(default=True)   #  <SRVmanaged></SRVmanaged>
    os = models.CharField(max_length=100)     #  <os>Windows2008R2managed</os>
    cpu = models.IntegerField('CPU')   #  <cpu>4</cpu>
    ram = models.IntegerField('RAM')    #  <ram>8</ram>
    #disk_space = models.CharField(max_length=100)  #  <diskspace>disk0=100 GB ;</diskspace>
    regulated_data = models.BooleanField(default=False)    #  <MWregulateddata></MWregulateddata>
    non_regulated_data = models.BooleanField(default=False)   #   <MWnonregulateddata></MWnonregulateddata>
    replicated = models.BooleanField(default=True)

    on_call = models.PositiveSmallIntegerField(null=True, choices=ON_CALL_CHOICES)   #<monitoringsystem>businesshours</monitoringsystem>
    in_service = models.BooleanField(default=True)   #<servicestatus>Ended</servicestatus>

    firewall = models.CharField(max_length=100)
    backup = models.BooleanField(default=False)
    support_email = models.CharField(max_length=100)    #  <afterhoursemail>dpss-technology-management@umich.edu</afterhoursemail>
    support_phone = models.CharField(max_length=100)   #  <afterhoursphone>7346470657</afterhoursphone>
    backup_time = models.TimeField('Daily Backup Time', null=True)   #  <dailybackuptime>06:00 PM</dailybackuptime>
    patch_time = models.TimeField(null=True)    #  <patchingScheduleTime>01:00 AM</patchingScheduleTime>
    patch_day = models.PositiveSmallIntegerField(choices=DAY_CHOICES, default=0) #  <patchingScheduleDate>Sunday</patchingScheduleDate>
    reboot_time = models.TimeField(null=True)    #  <rebootScheduleTime>04:00 AM</rebootScheduleTime>
    reboot_day = models.PositiveSmallIntegerField(null=True, choices=DAY_CHOICES) #   <rebootScheduleDate>Sunday</rebootScheduleDate>
    domain = models.CharField(max_length=100)
    datacenter = models.CharField(max_length=100)
    firewall_requests = models.CharField(max_length=100)
    legacy_data = models.TextField()

  #<diskspaceEnd>disk0=100 GB ;</diskspaceEnd>
  #<recovery>delayed</recovery>
  #<MWregulateddatacheckboxe1>[[]]</MWregulateddatacheckboxe1>
  #<recoveryoptions>Yes</recoveryoptions>
  #<servicestatusdate></servicestatusdate>
  #<xmlSubscriptionKey>PS-VD-DIRECTORY-1</xmlSubscriptionKey>
  #<additionalneedspage4></additionalneedspage4>
  #<afterhourssupportpage4>No. dpss-technology-management@umich.edu 7346470657</afterhourssupportpage4>
  #<updateByRequest>85605</updateByRequest>
  #<nonregulateddataDetail>[[]]</nonregulateddataDetail>
  #<subscribedDate>2012-11-01T14:56:40-04:00</subscribedDate>
  #<ipsubnet>secure</ipsubnet>
  #<service>MiServer</service>
  #<processing>CPU=4 ;RAM=8 GB ;</processing>

    def __str__(self):
        return self.name


class ServerDisk(models.Model):
    server = models.ForeignKey(Server, related_name='disks', on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    size = models.IntegerField()

    def __str__(self):
        return self.name

class ServerData(models.Model):
    server = models.ForeignKey(Server, related_name='data', on_delete=models.CASCADE)
    code = models.CharField(max_length=5)


class Database(models.Model):
    name = models.CharField(max_length=80)
    legacy_data = models.TextField()

    def __str__(self):
        return self.name

  #<SRVmanaged>Non-Managed</SRVmanaged>
  #<monitoringsystem>businesshours</monitoringsystem>
  #<afterhoursphone>8675309</afterhoursphone>
  #<regulatedData>No, the user does not store any regulated sensitive data. </regulatedData>
  #<purpose>purpose of testing</purpose>
  #<nonregulatedData>I do not know, the user does not know if they will store non-regulated sensitive data on their workstation or network file servers </nonregulatedData>
  #<replicationopt>Yes</replicationopt>
  #<MDsharedordedicated>shared</MDsharedordedicated>
  #<servicestatus>Ended</servicestatus>
  #<MDauthmode>Windows only</MDauthmode>
  #<datatransfer>no</datatransfer>
  #<readOnlyAccessGrp></readOnlyAccessGrp>
  #<servicestatusdate>03/21/2013</servicestatusdate>
  #<xmlSubscriptionKey>mgohsmantest</xmlSubscriptionKey>
  #<devAccessGrp>STSTVII</devAccessGrp>
  #<applAccountName>appmgohsmantest</applAccountName>
  #<MDdedicateddatabaseconnectioninformation>test</MDdedicateddatabaseconnectioninformation>
  #<ram>2</ram>
  #<MDsharedreadonlyaccess></MDsharedreadonlyaccess>
  #<applAccountType>windows</applAccountType>
  #<cpu>1</cpu>
  #<afterhourssupportpage4>No. test@umich.edu</afterhourssupportpage4>
  #<updateByRequest>2200</updateByRequest>
  #<subscribedDate>2012-10-19T18:26:45-04:00</subscribedDate>
  #<instancename></instancename>
  #<compatability>2008</compatability>
  #<afterhoursemail>test@umich.edu</afterhoursemail>
  #<service>MiDatabase</service>
  #<name>mgohsmantest</name>
  #<databaseSize>25GB</databaseSize>
  #<MDdbcompatibility>2012</MDdbcompatibility>
  #<MDdevelopergroupname></MDdevelopergroupname>



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
            data['due_date'] = self.due_date

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

        try: 
            with connections['pinnacle'].cursor() as cursor:
                ponum = cursor.callfunc('um_osc_util_k.um_add_preorder_f', cx_Oracle.STRING , [json_data])

            self.order_reference = ponum
            self.save()
            
            self.add_attachments()

        except cx_Oracle.DatabaseError as e:
        #except Exception as e:
            LogItem().add_log_entry('Error', self.id, e)
            num = str(self.id)
            url = settings.SITE_URL + '/orders/integration/'  + num
            send_mail('SRS Order # ' + num + ' failed to submit', url, 'itscomm.information.systems@umich.edu', ['itscomm.information.systems@umich.edu'])


class Item(models.Model):
    description = models.CharField(max_length=100)
    create_date = models.DateTimeField('Date Created', auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    deptid = models.CharField(max_length=8)
    chartcom = models.ForeignKey(Chartcom, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    data = JSONField()
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
                self.submit_incident(route) 

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
            rec.delete()
        else:
            if action.service.id == 8:
                self.update_mibackup(rec)
            else:
                rec.owner = LDAPGroup().lookup( self.data['owner'] )
                rec.service = action.service
                rec.name = self.data.get('name','')
                rec.owner = LDAPGroup().lookup( self.data['owner'] )
                rec.size = self.data.get('size',0)
                rec.service = action.service

                print('rate for ', action.service.id)
                if action.service.id == 11:
                    rec.rate_id = 28
                    print(rec.rate_id, 'set for dd')
                else:
                    rec.rate_id = self.data.get('selectOptionType')

                rec.type = action.override['storage_type']
                rec.shortcode = self.data.get('shortcode')
                rec.uid = self.data.get('uid')
                rec.ad_group = self.data.get('ad_group')    
                if action.service.id == 7:
                    self.update_mistorage(rec)
                else:
                    self.update_arcts(rec)
                                    
                rec.save()

                if self.data.get('permittedHosts'):
                    rec.update_hosts(self.data.get('permittedHosts'))

    def submit_incident(self, route):
        client_id = settings.UM_API['CLIENT_ID']
        auth_token = settings.UM_API['AUTH_TOKEN']
        base_url = settings.UM_API['BASE_URL']

        headers = { 
            'Authorization': f'Basic {auth_token}',
            'accept': 'application/json'
            }

        url = f'{base_url}/um/it/oauth2/token?grant_type=client_credentials&scope=tdxticket'
        response = requests.post(url, headers=headers)
        response_token = json.loads(response.text)
        access_token = response_token.get('access_token')

        headers = {
            'X-IBM-Client-Id': client_id,
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json' 
            }

        text = self.data['reviewSummary']
        note = render_to_string('order/pinnacle_note.html', {'text': text, 'description': self.description})
 
        payload = route['constants']
        payload['Title'] = self.description
        payload['RequestorEmail'] = self.created_by.email
        payload['Description'] = f'{note}\n'

        data_string = json.dumps(payload)
        response = requests.post( base_url + '/um/it/31/tickets', data=data_string, headers=headers )
 
        self.external_reference_id = json.loads(response.text)['ID']
        self.save()   # Save incident number to item

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

        rec.nfs_group_id = self.data.get('nfs_group_id')

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
    instance = models.ForeignKey(ArcInstance, on_delete=models.PROTECT)
    ticket_id = models.PositiveIntegerField()
    status = models.CharField(max_length=10)
    data = JSONField()

    class Meta:
        db_table = 'order_item_ticket_v'
        managed = False

    def __str__(self):
        return str(self.ticket_id)