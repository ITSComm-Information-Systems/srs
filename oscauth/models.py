from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group


class Role(models.Model):  
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    role = models.CharField(max_length=30,unique=True)
    role_description = models.CharField(max_length=1000)
    grantable_by_dept = models.BooleanField(default = False)
    active = models.BooleanField(default=True)
    inactivation_date = models.DateTimeField('Date Inactivated', blank=True, null=True)
    create_date = models.DateTimeField('Date Created', auto_now_add=True)
    created_by = models.CharField(max_length=150, default='Not implemented')
    last_update_date = models.DateTimeField('Last Date Updated', auto_now=True)
    last_updated_by = models.CharField(max_length=150, default='Not implemented')

    def __str__(self):
        return self.role

    def save(self, *args, **kwargs):
        if not self.active and self.inactivation_date is None:
            self.inactivation_date = timezone.now()
        elif self.active and self.inactivation_date is not None:
            self.inactivation_date = None
        if self.pk is None:
            self.created_by = 'Not implemented'
            self.last_updated_by = 'Not implemented'
        elif self.pk is not None:
            self.last_updated_by = 'Not implemented'
        super(Role, self).save(*args, **kwargs)

    class Meta:
        db_table = 'auth_role'
        permissions = [
            ('can_administer_access_all', 'Can Modify All Access Privileges'),
            ('can_administer_access', 'Can Modify Access Privileges (except proxy)'),
            ('can_order', 'All ordering functions'),
            ('can_report', 'Can run reports'),
            ('can_impersonate', 'Can Impersonate'),            
        ]

class AuthUserDeptV(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    codename = models.CharField(max_length=20, blank=True)
    dept = models.CharField(max_length=10, blank=True, primary_key=True)

    class Meta:
        managed = False
        db_table = 'auth_user_dept_v'

class AuthUserDept(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    dept = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = 'auth_user_dept'
        unique_together = (("user", "group", "dept"),)

    def get_order_departments(self):
        return AuthUserDeptV.objects.filter(user_id=self,codename='can_order')


class Grantor(models.Model):
    grantor_role = models.ForeignKey(Group, on_delete=models.PROTECT)
    granted_role = models.ForeignKey(Role, on_delete=models.PROTECT)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.role

    class Meta:
        db_table = 'auth_grantor'
        unique_together = (("grantor_role", "granted_role"),)
