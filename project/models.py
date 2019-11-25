from django.db import models
from django.contrib.auth.models import User

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