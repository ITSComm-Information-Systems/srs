from django.db import models

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


