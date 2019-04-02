from django.db import models
from oscauth.models import Role

class Step(models.Model):
    name = models.CharField(max_length=20)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    label = models.CharField(max_length=80)

    def __str__(self):
        return self.label

class Product(models.Model):
    name = models.CharField(max_length=80)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    description = models.TextField()
    active = models.BooleanField(default=True)
    #picture = models.FileField()

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=20)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class FeatureCategory(models.Model):
    name = models.CharField(max_length=40)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

class Feature(models.Model):
    name = models.CharField(max_length=40)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    category = models.ManyToManyField(FeatureCategory)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):        
        return self.name

class Action(models.Model):
    ROUTE_CHOICES = (
        ('P', 'Preorder'),
        ('I', 'Incident'),
        ('E', 'Email'),
    )

    TYPE_CHOICES = (
        ('A', 'Add'),
        ('M', 'Modify'),
        ('D', 'Disconnect'),
        ('E', 'Equipment'),
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='A')
    name = models.CharField(max_length=100)
    display_seq_no = models.PositiveIntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)    
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    steps = models.ManyToManyField(Step)
    route = models.CharField(max_length=1, choices=ROUTE_CHOICES, default='P')
    destination = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.name 

class Cart(models.Model):
    number = models.IntegerField()
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.description

class Item(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    service = models.CharField(max_length=10) 
    service_action = models.CharField(max_length=10) 
    service_detail = models.CharField(max_length=10) 
    status = models.CharField(max_length=10) 


class PinnServiceProfile(models.Model):
    deptid = models.CharField(max_length=20, primary_key=True) 
    service_number = models.CharField(max_length=20) 
    service_type = models.CharField(max_length=20) 
    
    def __str__(self):
        return self.service_number
    
    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"um_osc_service_profile_v'
