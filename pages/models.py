#   \osc\pages\models.py
from django.db import models

from django.db.models.signals import class_prepared
# Create your models here.

def add_db_prefix(sender, **kwargs):
     if sender._meta.db_table == 'django_migrations' or \
          sender._meta.db_table[:3] in ['um_','PS_','PIN']:
               return

     # Add SRS_ prefix to all table in PINN_CUSTOM
     prefix = 'SRS_'

     if isinstance(prefix, dict):
          app_label = sender._meta.app_label.lower() 
          sender_name = sender._meta.object_name.lower()
          full_name = app_label + "." + sender_name
          if full_name in prefix:
               prefix = prefix[full_name]
          elif app_label in prefix:
               prefix = prefix[app_label]
          else:
               prefix = prefix.get(None, None)
     if prefix:
          sender._meta.db_table = prefix + sender._meta.db_table

class_prepared.connect(add_db_prefix)

class Page(models.Model):
    title = models.CharField(max_length=60)
    permalink = models.CharField(unique=True, max_length=12)
    update_date = models.DateTimeField(auto_now=True)
    bodytext = models.TextField()
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)

    class Meta:
        ordering = ('display_seq_no', 'title')
       
    def __str__(self):
        return self.title