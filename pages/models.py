#   \osc\pages\models.py
from django.db import models

# Create your models here.

class Page(models.Model):
    title = models.CharField(max_length=60)
    permalink = models.CharField(unique=True, max_length=12)
    update_date = models.DateTimeField()
    bodytext = models.TextField()
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)

    class Meta:
        ordering = ('display_seq_no',)
       
    def __str__(self):
        return self.title