from sqlite3 import Timestamp
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

from django.forms import CharField, JSONField
from project.integrations import ShortCodesAPI
from django.db.models.signals import class_prepared

from django.template import Template, Context
from datetime import timedelta
from softphone.models import next_cut_date

def add_db_prefix(sender, **kwargs):
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
          if not sender._meta.db_table[:3] in ['um_','PS_','PIN']:
               #print('um_', sender._meta.db_table[:3])
               sender._meta.db_table = prefix + sender._meta.db_table

#class_prepared.connect(add_db_prefix)


def validate_shortcode(value):

     if not re.search("\d{6}", value):
          raise ValidationError(f'Please enter a six digit shortcode.')
     else:
          try:
               api = ShortCodesAPI()
               request = api.get_shortcode(value)
               if request.ok:
                    json = request.json()
                    shortcode = json['ShortCodes']['ShortCode']
                    descr = shortcode['shortCodeDescription']
                    status = shortcode['ShortCodeStatusDescription']
               else:
                    print('error getting shortcode')
                    status = 'Open'
          except:
               raise ValidationError(f'ShortCode {value} Not Found.')

     if status != 'Open':
          raise ValidationError(f'ShortCode {value} is {status}.')



# This view uses the Pinnacle location table and includes locations added by ITS staff
#  as well as the official builfing codes from MPathways
class Test(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   url  = models.CharField(max_length=500)
   result = models.IntegerField(default=200)

   def __str__(self):
        return self.url
   class Meta:
        verbose_name_plural = "Tests"


class ShortCodeField(models.CharField):

    description = "Six digit shortcode"
    help_text = 'Chartfield/Chartcom'

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 6
        #kwargs['validators']=[validate_shortcode]
        kwargs['help_text']='Six digit shortcode for billing purposes.'

        super().__init__(*args, **kwargs)


class ActionLog(models.Model):
     timestamp = models.DateTimeField()
     user = models.CharField(max_length=20)
     url = models.CharField(max_length=200)
     data = models.JSONField()


class ChoiceManager(models.Manager):

     def get_choices(self, code):

          group_list = []
          for optgroup in Choice.objects.filter(parent__code=code, active=True).order_by('sequence'):

               option_list = []
               value = optgroup.label

               for option in Choice.objects.filter(parent=optgroup.id, active=True).order_by('sequence'):
                    option_list.append((option.id, option.label))

               if option_list == []:
                    value = optgroup.id
                    option_list = optgroup.label

               group_list.append((value, option_list))

          return group_list


class Choice(models.Model):
     active = models.BooleanField(default=True)
     code = models.CharField(max_length=80)
     sequence = models.PositiveSmallIntegerField()
     parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
     label = models.CharField(max_length=100)
     objects = ChoiceManager()
     
     def __str__(self):
          return self.label


class ChoiceTag(models.Model):
     code = models.CharField(max_length=20)
     label = models.CharField(max_length=100)

     def __str__(self):
          return self.code

class Webhooks(models.Model):
     sender = models.CharField(max_length=20, null=True) #uniqname
     preorder = models.CharField(max_length=50, null=True) #used to find estimate
     device_id = models.IntegerField(null=True) #what gets sent in request to netbox
     name = models.CharField(max_length=50, null=True) #ap-LBME-1350-W, aka location
     success = models.BooleanField(default=False) #was it added to BOM
     issue = models.CharField(max_length=50, default='no issue')
     emailed = models.BooleanField(default=False) #was it sent in email
     timestamp = models.DateTimeField(auto_now_add=True)
     added = models.CharField(max_length=255, null=True)
     skipped = models.CharField(max_length=255, null=True)


class Email(models.Model):
     code = models.CharField(max_length=20)
     sender = models.CharField(max_length=100)
     to = models.CharField(max_length=100)
     cc = models.CharField(max_length=100, blank=True, null=True)
     bcc = models.CharField(max_length=100, blank=True, null=True)
     subject = models.CharField(max_length=100)
     body = models.TextField()

     def __str__(self):
          return self.code

     def render_subject(self):
          cut_date = next_cut_date()
          week_of = cut_date - timedelta(days = 3)

          context = {'cut_date': cut_date, 'week_of': week_of}
          return Template(self.subject).render(Context(context))

     def render_body(self):
          cut_date = next_cut_date()
          week_of = cut_date - timedelta(days = 3)

          context = {'cut_date': cut_date, 'week_of': week_of}
          return Template(self.body).render(Context(context))
