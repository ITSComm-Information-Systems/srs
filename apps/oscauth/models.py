from django.db import models

class ExternalModel(models.Model):
  class Meta:
    managed = False
    abstract = True

class Role(models.Model):
    role = models.CharField(primary_key=True, max_length=30, db_column='role')
    role_desc = models.CharField(max_length=2000)
    #is_dept_manager = models.NullBooleanField()
    #can_add_proxy = models.CharField(max_length=1)
    #can_add_nonproxy_users = models.CharField(max_length=1)
    #can_submit_orders = models.CharField(max_length=1)
    #can_run_reports = models.CharField(max_length=1)
    
    list_display = ('first_name', 'last_name')
    
    def __str__(self):
        return self.role

    class Meta(ExternalModel.Meta):
        db_table = 'PINN_CUSTOM\".\"UM_OSC_VALID_ROLES'
        #ordering = ['account', 'charge_group', 'description']


class Test(models.Model):
    name = models.CharField(max_length=200)
    descr = models.CharField(max_length=200)

class Person(models.Model):
    name = models.CharField(max_length=200)
    descr = models.CharField(max_length=200)



