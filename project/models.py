from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


def validate_shortcode(value):

     if re.search("\d{6}", value):
          print('todo lookup shortcode')
     else:
          raise ValidationError(f'Please enter a six digit shortcode.')


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
        kwargs['validators']=[validate_shortcode]
        kwargs['help_text']='Six digit shortcode for billing purposes.'

        super().__init__(*args, **kwargs)