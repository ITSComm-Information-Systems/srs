from django.contrib.postgres.fields import JSONField
from django.db import models
from oscauth.models import Role
from project.pinnmodels import UmOscPreorderApiAbstract


class Configuration(models.Model):   #Common fields for configuration models
    name = models.CharField(max_length=20)
    label = models.CharField(max_length=100)
    display_seq_no = models.PositiveIntegerField()

    def __str__(self):
        return self.label

    class Meta:
        abstract = True 


class Step(Configuration):
    FORM_CHOICES = (
        ('', ''),
        ('LocationForm', 'Location'),
        ('EquipmentForm', 'Equipment'),
        ('NewLocationForm', 'New Location'),
        ('AddlInfoForm', 'Additional Information'),
        ('ReviewForm', 'Review'),
        ('ChartfieldForm', 'Chartfield'),
        ('RestrictionsForm', 'Restrictions'),
        ('FeaturesForm', 'Features'),

    )

    custom_form = models.CharField(blank=True, max_length=20, choices=FORM_CHOICES)


class Element(Configuration):
    ELEMENT_CHOICES = (
        ('', ''),
        ('YN', 'Yes/No'),
        ('Radio', 'Radio'),
        ('ST', 'String'),
        ('NU', 'Number'),
        ('PH', 'Phone Set Type'),
    )

    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=ELEMENT_CHOICES)
    attributes = models.CharField(blank=True, max_length=100)
    target = models.CharField(max_length=80)


class ProductCategory(Configuration):
    
    class Meta:
        verbose_name_plural = "Product Categories"


class Product(Configuration):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    active = models.BooleanField(default=True)
    picture = models.FileField(upload_to='pictures',blank=True, null=True)


class Service(Configuration):
    active = models.BooleanField(default=True)


class FeatureCategory(models.Model):
    name = models.CharField(max_length=40)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Feature Categories"


class Feature(Configuration):
    TYPE_CHOICES = (
        ('STD', 'Standard'),
        ('OPT', 'Optional'),
        ('SPD', 'Speed Call'),
        ('VM', 'Voice Mail'),
    )

    name = models.CharField(max_length=40)
    category = models.ManyToManyField(FeatureCategory)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)


class Restriction(Configuration):
    #label = models.CharField(max_length=40)
    #display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    category = models.ManyToManyField(FeatureCategory)

    def __str__(self):
        return self.label


class Action(Configuration):
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
    #label = models.CharField(max_length=100)
    #display_seq_no = models.PositiveIntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)    
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    steps = models.ManyToManyField(Step)
    route = models.CharField(max_length=1, choices=ROUTE_CHOICES, default='P')
    destination = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.label 


class Constant(models.Model):
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    field = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.field 


class Cart(models.Model):
    number = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    username = models.CharField(max_length=8)

    def __str__(self):
        return self.description
    
    def leppard(self):
        pour=['me']
        pour.append('sugar')


class Item(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    data = JSONField()

    def __str__(self):
        return self.description
