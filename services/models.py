from django.db import models
from django.forms import BooleanField
from django.utils import timezone
from project.models import Choice
from oscauth.models import LDAPGroup
from django.contrib.auth.models import User


class Status(models.TextChoices):
    ACTIVE = 'A', 'Active'
    ENDED = 'E', 'Ended'
    PENDING = 'P', 'Pending'


class Cloud(models.Model):    # Core class for common fields/methods
    instance_label = 'Instance'
    account_id = models.CharField(max_length=30, default='TBD')
    status = models.CharField(max_length=1, choices = Status.choices, default=Status.ACTIVE)
    owner = models.ForeignKey(LDAPGroup, on_delete=models.CASCADE, null=True)
    requestor = models.CharField(max_length=8)
    security_contact = models.CharField(max_length=80)
    billing_contact = models.CharField(max_length=80)
    shortcode = models.CharField(max_length=6)
    vpn = BooleanField()
    created_date = models.DateField(auto_now=True)

    regulated_data = models.ManyToManyField(Choice, blank=True, limit_choices_to={"parent__code": "REGULATED_SENSITIVE_DATA"},
        related_name="%(class)s_reg_related")
        #related_query_name="%(app_label)s_%(class)ss")

    non_regulated_data = models.ManyToManyField(Choice, blank=True, limit_choices_to={"parent__code": "NON_REGULATED_SENSITIVE_DATA"},
        related_name="%(class)s_nonreg_related")
        #related_query_name="%(app_label)s_%(class)ss")

    def __str__(self):
        return self.account_id

    class Meta:
        abstract = True 


class AWS(Cloud):
    instance_label = 'Account'
    data_classification = models.CharField(max_length=10, blank=True, null=True)
    egress_waiver = models.BooleanField()
    version = models.ForeignKey(Choice, on_delete=models.CASCADE, limit_choices_to={"parent__code": "AWS_VERSION"}, default=132) 

    class Meta:
        verbose_name = 'Amazon Web Services Account'


class GCPAccount(Cloud):
    account_id = models.CharField(max_length=30, verbose_name='Billing ID', default='TBD')
    requestor = None
    security_contact = None
    vpn = None
    created_date = None
    regulated_data = None
    non_regulated_data = None

    class Meta:
        verbose_name = 'Google Cloud Platform Account'


class GCP(Cloud):
    instance_label = 'Project'
    owner = models.ForeignKey(LDAPGroup, on_delete=models.CASCADE, null=True, related_name='project_owner')
    account_id = None
    gcp_account = models.ForeignKey(GCPAccount, on_delete=models.CASCADE)
    shortcode = None
    billing_contact = None
    project_id = models.CharField(max_length=40)

    class Meta:
        verbose_name = 'Google Cloud Platform Project'

    def __str__(self):
        return self.project_id

    @property
    def account_id(self):
        return self.gcp_account.account_id

    @property
    def shortcode(self):
        return self.gcp_account.shortcode

    def save(self, *args, **kwargs):
        if self.gcp_account_id == None:
            acct = GCPAccount.objects.create()
            self.gcp_account_id = acct.id

        super().save(*args, **kwargs)  # Call the "real" save() method.


class Azure(Cloud):
    instance_label = 'Subscription'
    account_id = models.CharField(max_length=40, verbose_name='Subscription ID', default='TBD')
    name = models.CharField(max_length=40, default='TBD')
    vpn_tier = models.ForeignKey(Choice, blank=True, null=True, on_delete=models.CASCADE, limit_choices_to={"parent__code": "VPN_TIER"})

    class Meta:
        verbose_name = 'Azure Subscription'


class Container(Cloud):
    SIZE_CHOICES = (
        ('sm_container', 'SMALL, up to 1GB RAM ($0.02/hr)'),
        ('med_container', 'Upgrade to MEDIUM, 1-4GB RAM ($0.04/hr)'),
        ('lg_container', 'Upgrade to LARGE, 4-8GB RAM ($0.08/hr)'))

    DATABASE_TYPE_CHOICES = (
        ('MARIADB', 'MariaDB'),
        ('POSTGRES', 'PostGres'),
    )

    DATABASE_ADDON_CHOICES = (
        ('NONE', 'No Database'),
        ('SHARED', 'Shared Database'),
        ('DEDICATED', 'Dedicated Database')
    )

    instance_label = 'Project'
    project_name = models.CharField(max_length=40)
    project_description = models.TextField()
    size = models.CharField(max_length=20, choices=SIZE_CHOICES,
                            verbose_name='Container Size',
                            help_text="This sets the upper limit of CPU and RAM available for your containerized applications. This can be changed later via request to Container Service staff. More information about container sizes and rates can be found here: <a href='https://its.umich.edu/computing/virtualization-cloud/container-service/pricing' target='_blank'>https://its.umich.edu/computing/virtualization-cloud/container-service/pricing</a>")
    database_type = models.CharField(max_length=10, choices=DATABASE_TYPE_CHOICES, null=True)
    database = models.CharField(max_length=10, choices=DATABASE_ADDON_CHOICES,
                            help_text='The MiDatabase team manages Amazon RDS databases for Container Service customers. Databases in shared instances are available at no cost. The cost of dedicated RDS instances are passed through to the shortcode provided.')
    backup = models.CharField(max_length=6)
    course_info = models.CharField(max_length=20)
    admin_group = models.CharField(max_length=80)

    class Meta:
        managed = False   # We don't want a real table in Oracle but abstract models can't be instantiated.

class CloudImage(Cloud):
    instance_label = 'Image Name'
    account_id = models.CharField(max_length=30, verbose_name='Image Name', default='TBD')
    cpu = models.CharField(max_length=4)
    cpu_cost = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    memory = models.CharField(max_length=4)
    memory_cost = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    storage= models.CharField(max_length=8)
    storage_cost = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    gpu = models.BooleanField(blank=True, null=True)
    gpu_cost = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)

    class Meta:
        verbose_name = 'MiServer Cloud Desktop Image'
        db_table = "srs_services_clouddimagetest"



class CloudDesktop(Cloud):
    instance_label = 'Pool Name'
    account_id = models.CharField(max_length=30, verbose_name='Pool Name', default='TBD')
    pool_maximum = models.IntegerField()
    pool_cost = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    ad_access_groups = models.CharField(max_length=100)
    sla = models.BooleanField()
    persistent_vm = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'MiServer Cloud Desktop Pool'
        db_table = "srs_services_clouddesktoptest"

class Service():
    aws = AWS
    gcp = GCP
    azure = Azure
    gcpaccount = GCPAccount
    clouddesktop = CloudDesktop
    container = Container