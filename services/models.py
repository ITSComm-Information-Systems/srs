from django.db import models
from django.forms import BooleanField
from django.utils import timezone
from project.models import Choice
from oscauth.models import LDAPGroup
from django.contrib.auth.models import User


class Cloud(models.Model):    # Core class for common fields/methods
    account_id = models.CharField(max_length=30)
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
    data_classification = models.CharField(max_length=10, blank=True, null=True)
    egress_waiver = models.BooleanField()
    version = models.ForeignKey(Choice, on_delete=models.CASCADE, limit_choices_to={"parent__code": "AWS_VERSION"}) 

    class Meta:
        verbose_name_plural = 'AWS Accounts'


class GCPAccount(Cloud):
    account_id = models.CharField(max_length=30, verbose_name='Billing ID')
    owner = None
    requestor = None
    security_contact = None
    vpn = None
    created_date = None
    regulated_data = None
    non_regulated_data = None

    class Meta:
        verbose_name_plural = 'GCP Accounts'


class GCP(Cloud):
    account_id = None
    gcp_account = models.ForeignKey(GCPAccount, on_delete=models.CASCADE)
    shortcode = None
    billing_contact = None
    project_id = models.CharField(max_length=40)

    def __str__(self):
        return self.project_id

class Azure(Cloud):
    account_id = models.CharField(max_length=40, verbose_name='Subscription ID')
    name = models.CharField(max_length=40)


    class Meta:
        verbose_name_plural = 'Azure Subscriptions'
        
