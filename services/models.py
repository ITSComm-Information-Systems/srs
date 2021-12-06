from django.db import models
from django.utils import timezone
from project.models import Choice
from oscauth.models import LDAPGroup
from django.contrib.auth.models import User


class AWSAccount(models.Model):
    account_id = models.CharField(max_length=30)
    billing_contact = models.CharField(max_length=8)
    shortcode = models.CharField(max_length=6)
    requestor = models.CharField(max_length=8)
    created_date = models.DateTimeField(default=timezone.now, null=True)
    data_classification = models.CharField(max_length=10, blank=True, null=True)
    regulated_data = models.ManyToManyField(Choice, blank=True, limit_choices_to={"parent__code": "REGULATED_SENSITIVE_DATA"}, related_name='aws_regulated')
    non_regulated_data = models.ManyToManyField(Choice, blank=True, limit_choices_to={"parent__code": "NON_REGULATED_SENSITIVE_DATA"}, related_name='aws_nonreg')
    egress_waiver = models.BooleanField()
    owner = models.ForeignKey(LDAPGroup, on_delete=models.CASCADE, null=True)
    security_contact = models.CharField(max_length=30)
    version = models.ForeignKey(Choice, on_delete=models.CASCADE, limit_choices_to={"parent__code": "AWS_VERSION"}) 
    vpn = models.BooleanField()

    def __str__(self):
        return self.account_id
