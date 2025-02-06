from django.db import models

class DepartmentalTelephoneServiceMetricsClickLog(models.Model):

    clicked_at = models.DateTimeField(auto_now_add=True)
    clicked_by = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.clicked_by} clicked at {self.clicked_at}'