from django.db import models

class Step(models.Model):
    name = models.CharField(max_length=20)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Workflow(models.Model):
    name = models.CharField(max_length=20)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name 

class Product(models.Model):
    name = models.CharField(max_length=20)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    description = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    picture = models.ImageField()

    def __str__(self):
        return self.name

class Action(models.Model):
    name = models.CharField(max_length=20)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=20)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    active = models.BooleanField(default=True)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    actions = models.ManyToManyField(Action)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return self.name 

class Cart(models.Model):
    #user = models.CharField(max_length=8)
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


