from sqlite3 import Timestamp
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.forms import CharField, JSONField
from project.integrations import ShortCodesAPI
from django.db.models.signals import class_prepared

from django.template import Template, Context
from datetime import timedelta
from softphone.models import next_cut_date


def validate_shortcode(value):

     if not re.fullmatch(r"\d{6}", value):
          raise ValidationError('Please enter a six digit shortcode.')
     else:
          try:
               api = ShortCodesAPI()
               request = api.get_shortcode(value)
               if request.ok:
                    json = request.json()
                    shortcode = json['ShortCodes']['ShortCode'][0]
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


class Unity(models.Model):
     username = models.CharField(max_length=8)
     temp_password = models.CharField(max_length=100)
     temp_pin = models.CharField(max_length=10)
     phone_number = models.CharField(max_length=20)

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


class ChoiceSet(models.Model):
    """
    The domain/category, e.g. SERVER_OS, BACKUP_TIME, STORAGE_TIER.
    """
    code = models.CharField(max_length=80, unique=True)   # SERVER_OS
    label = models.CharField(max_length=120)              # "Server Operating System"
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Choice(models.Model):
     active = models.BooleanField(default=True)
     code = models.CharField(max_length=80)
     sequence = models.PositiveSmallIntegerField()
     parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
     set = models.ForeignKey(ChoiceSet, on_delete=models.CASCADE)
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
     team_shared_email = 'itscomm.information.systems.shared.account@umich.edu'
     context = {}
     reply_to = None

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
          return Template(self.subject).render(Context(self.context))

     def render_body(self):
          return Template(self.body).render(Context(self.context))

     def send(self):
          text_message = self.subject
          subject = self.subject

          body = Template(self.body).render(Context(self.context))

          if settings.ENVIRONMENT != 'Production':
               print('Non-prod, do not send to:', self.to)
               self.to = 'djamison@umich.edu'
               self.cc = ''
               self.bcc = self.team_shared_email
               subject = f'{settings.ENVIRONMENT} - {self.subject}'

          # Send Distribution List to Leads
          msg = EmailMultiAlternatives(subject, text_message, self.sender, [self.to], cc=[self.cc], bcc=[self.bcc], reply_to=[self.reply_to],
                                       headers = {'srs_code': self.code})
          msg.attach_alternative(body, "text/html")
          msg.send()
