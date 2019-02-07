from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'service'

class Action(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'service_action'

class Attribute(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    required = models.BooleanField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'service_attribute'