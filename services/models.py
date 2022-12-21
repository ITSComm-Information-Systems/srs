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
        


class Service():
    aws = AWS
    gcp = GCP
    azure = Azure
    gcpaccount = GCPAccount

class VirtualDesktop(models.Model):
    shortcode = models.CharField(max_length=6)
    pool_name = models.CharField(max_length=100)
    gpu = models.BooleanField()
    memory = models.CharField(max_length=4)
    cpu = models.CharField(max_length=4)
    storage = models.CharField(max_length=8)
    individual_cost = models.DecimalField(max_digits=10, decimal_places=2)
    num_computers = models.CharField(max_length=100)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    admin_group = models.CharField(max_length=100)
        
    def __str__(self):
        return self.pool_name


# class DesktopRequest(models.Model):
#     CUSTOMER_CHOICES = (('N', 'New'),('E', 'Existing'))
#     NETWORK_CHOICES = (('N', 'New'),('E', 'Existing'))
#     BASE_IMAGE_CHOICES = (('N', 'New'),('E', 'Existing'))
#     INITIAL_IMAGE_CHOICES = (('B', 'Base'),('S', 'MiDesktop Standard Image'))
#     OS_CHOICES = (('W10','Windows 10'),('',''))

#     user = models.ForeignKey(LDAPGroup, on_delete=models.CASCADE, null=True)
#     # mcom_group = models.ForeignKey(LDAPGroup, on_delete=models.CASCADE, null=True, related_name='admin_group')
#     shortcode = models.CharField(max_length=6)
#     customer = models.CharField(max_length=1, choices=CUSTOMER_CHOICES)
#     network = models.CharField(max_length=1, choices=NETWORK_CHOICES)
#     base_image = models.CharField(max_length=1, choices=BASE_IMAGE_CHOICES)
#     initial_image = models.CharField(max_length=1, choices=INITIAL_IMAGE_CHOICES)
#     os = models.CharField(max_length=3, choices=OS_CHOICES)

#     cpu = models.PositiveSmallIntegerField()
#     ram = models.PositiveSmallIntegerField()
#     disk_space = models.PositiveSmallIntegerField()
#     gpu = models.BooleanField()
#     pool_display_name = models.CharField(max_length=60)

# class Pool(models.Model):
#     owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
#     display_name = models.CharField(max_length=100)
#     base_image = models.CharField(
#         max_length=10,
#         choices=[("New", "New"), ("Existing", "Existing")],
#     )
#     initial_image = models.CharField(
#         max_length=20,
#         choices=[("Blank", "Blank"), ("MiDesktop Standard Image", "MiDesktop Standard Image")],
#     )
#     network = models.CharField(
#         max_length=10,
#         choices=[("New", "New"), ("Existing", "Existing")],
#     )
#     size = models.IntegerField()
#     min_num_desktops = models.IntegerField()
#     num_powered_desktops = models.IntegerField()
#     active_directory_container_OU = models.CharField(max_length=100)
#     authorized_AD_groups = models.CharField(max_length=100)
#     details = models.TextField()
#     sle_accepted = models.BooleanField()
    
#     def __str__(self):
#         return self


# class Desktop(models.Model):
#     pool_name = models.ForeignKey(Pool, on_delete=models.CASCADE)
#     os = models.CharField(max_length=50)
#     cpu = models.IntegerField()
#     ram = models.IntegerField()
#     disk_space = models.IntegerField()
#     gpu = models.BooleanField()
#     auto_logout = models.CharField(
#         max_length=11,
#         choices=[("Never", "Never"), ("Immediately", "Immediately")],
#     )
#     auth_method = models.CharField(
#         max_length=10,
#         choices=[("Non-2FA", "Non-2FA"), ("2FA Public", "2FA Public"), ("2FA Local", "2FA Local")],
#     )
