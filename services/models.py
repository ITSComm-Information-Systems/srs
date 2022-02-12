from django.db import models
from django.forms import BooleanField
from django.utils import timezone
from project.models import Choice
from oscauth.models import LDAPGroup
from django.contrib.auth.models import User


class Cloud(models.Model):    # Core class for common fields/methods
    account_label = 'Account ID'
    account_id = models.CharField(max_length=30, verbose_name=account_label)
    owner = models.ForeignKey(LDAPGroup, on_delete=models.CASCADE, null=True)
    requestor = models.CharField(max_length=8)
    security_contact = models.CharField(max_length=80)
    billing_contact = models.CharField(max_length=80)
    shortcode = models.CharField(max_length=6)
    vpn = BooleanField()
    created_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.account_id

    class Meta:
        abstract = True 


class AWS(Cloud):
    #account_id = models.CharField(max_length=30)
    data_classification = models.CharField(max_length=10, blank=True, null=True)
    regulated_data = models.ManyToManyField(Choice, blank=True, limit_choices_to={"parent__code": "REGULATED_SENSITIVE_DATA"}, related_name='aws_regulated')
    non_regulated_data = models.ManyToManyField(Choice, blank=True, limit_choices_to={"parent__code": "NON_REGULATED_SENSITIVE_DATA"}, related_name='aws_nonreg')
    egress_waiver = models.BooleanField()
    version = models.ForeignKey(Choice, on_delete=models.CASCADE, limit_choices_to={"parent__code": "AWS_VERSION"}) 

    class Meta:
        verbose_name_plural = 'AWS Accounts'


class GCP(Cloud):
    account_label = 'Billing ID'
    pass

    class Meta:
        verbose_name_plural = 'GCP Accounts'


class GCPProject(models.Model):
    project_id = models.CharField(max_length=40)
    account = models.ForeignKey(GCP, on_delete=models.CASCADE)



class Azure(Cloud):
    account_label = 'Subscription ID'
    #subscription_id = models.CharField(max_length=40)
    name = models.CharField(max_length=40)

    class Meta:
        verbose_name_plural = 'Azure Accounts'