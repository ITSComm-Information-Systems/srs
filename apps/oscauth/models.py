from django.db import models

class ExternalModel(models.Model):
  class Meta:
    managed = False
    abstract = True

class Role(models.Model):
    role = models.CharField(primary_key=True, max_length=30, db_column='role')
    role_description = models.CharField(max_length=2000)
    is_dept_manager = models.CharField(max_length=1)
    can_add_proxy = models.CharField(max_length=1)
    can_add_nonproxy_users = models.CharField(max_length=1)
    can_submit_orders = models.CharField(max_length=1)
    can_run_reports = models.CharField(max_length=1)
    
    list_display = ('first_name', 'last_name')
    
    def __str__(self):
        return self.role

    class Meta(ExternalModel.Meta):
        db_table = 'PINN_CUSTOM\".\"UM_OSC_VALID_ROLES'
        #ordering = ['account', 'charge_group', 'description']


class DBRouter(object):
  def db_for_read(self, model, **hints):

    if model._meta.db_table == 'PINN_CUSTOM"."UM_ECOMM_DEPT_UNITS_REPT':
      return 'pinnacle'
    elif model._meta.db_table == 'PINN_CUSTOM"."UM_AUTHORIZED_DEPT_USERS':
      return 'pinnacle'
    return 'default'

  def db_for_write(self, model, **hints):
    return 'default'

  def allow_migrate(self, db, app_label, **hints):
    if db == "pinnacle":
      return False
    else:
      return True
