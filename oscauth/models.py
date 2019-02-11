from django.db import models

# Create your models here.
class Role(models.Model):
    display_seq_no = models.IntegerField(default=0)
    role = models.CharField(max_length=30)
    role_description = models.CharField(max_length=1000)
    active = models.BooleanField
    inactivation_date = models.DateTimeField
    create_date = models.DateTimeField
    created_by = models.CharField(max_length=10)
    last_update_date = models.DateTimeField
    last_updated_by = models.CharField(max_length=10)

class Privilege(models.Model):
    display_seq_no = models.IntegerField(default=0)
    privilege = models.CharField(max_length=30)
    privilege_description = models.CharField(max_length=1000)
    active = models.BooleanField
    inactivation_date = models.DateTimeField
    create_date = models.DateTimeField
    created_by = models.CharField(max_length=10)
    last_update_date = models.DateTimeField
    last_updated_by = models.CharField(max_length=10)

class Restriction(models.Model):
    display_seq_no = models.IntegerField(default=0)
    restriction_type = models.CharField(max_length=10)
    restriction = models.CharField(max_length=30)
    restriction_description = models.CharField(max_length=1000)
    active = models.BooleanField
    inactivation_date = models.DateTimeField
    create_date = models.DateTimeField
    created_by = models.CharField(max_length=10)
    last_update_date = models.DateTimeField
    last_updated_by = models.CharField(max_length=10)

class RolePrivilege(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    privilege = models.ForeignKey(Privilege, on_delete=models.CASCADE)
    restriction_permitted = models.BooleanField
    grantable_privilege = models.BooleanField
    active = models.BooleanField
    inactivation_date = models.DateTimeField
    create_date = models.DateTimeField
    created_by = models.CharField(max_length=10)
    last_update_date = models.DateTimeField
    last_updated_by = models.CharField(max_length=10)

class RolePrivRestriction(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    privilege = models.ForeignKey(Privilege, on_delete=models.CASCADE)
    restriction = models.ForeignKey(Restriction, on_delete=models.CASCADE)
    active = models.BooleanField
    inactivation_date = models.DateTimeField
    create_date = models.DateTimeField
    created_by = models.CharField(max_length=10)
    last_update_date = models.DateTimeField
    last_updated_by = models.CharField(max_length=10)

