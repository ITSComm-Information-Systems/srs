from django.db import models
import json

from django.db.models.fields import IntegerField


class Category(models.Model):
    OTHER = 49
    CONFERENCE_ROOM = 47
    
    sequence = models.PositiveSmallIntegerField(null=True, blank=True)
    code = models.CharField(max_length=20)
    label = models.CharField(max_length=80)

    class Meta:
        verbose_name_plural = "Categories"
        #db_table = 'um_softphone_category'
        db_table = 'PINN_CUSTOM\".\"um_softphone_category'
        managed = False

    def __str__(self):
        return self.label


class SelectionManager(models.Manager):

    def selections_made(self, dept_id):
        return SelectionV.objects.filter(dept_id=dept_id).count()

    def with_charges(self, dept_id, **kwargs):
        phone_list = []
        #charge_list = []
        phone = {}
        subid = 0

        if 'subscribers' in kwargs:
            subscriber_list = kwargs['subscribers']
            qry = SubscriberCharges.objects.filter(dept_id=dept_id, subscriber_id__in=subscriber_list).order_by('user_defined_id')
        else:
            qry = SubscriberCharges.objects.filter(dept_id=dept_id).order_by('user_defined_id')


        for charge in qry:
            if charge.subscriber_id != subid and subid != 0:
                phone_list.append(phone)
                phone = {}
                #charge_list = []

            phone['user'] = charge.current_uniqname
            phone['name'] = f'{charge.current_first_name} {charge.current_last_name}'
            phone['number'] = charge.user_defined_id
            phone['subscriber'] = charge.subscriber_id
            phone['charges'] = charge.charges

            phone['service_id'] = charge.service_id
            phone['service_number'] = charge.service_number

            if charge.building:                
                phone['location_id'] = charge.location_id
                phone['building_code'] = charge.building_code
                phone['building'] = charge.building
                phone['floor'] = charge.floor
                phone['room'] = charge.room
                phone['jack'] = charge.jack
                phone['cable_path_id'] = charge.cable_path_id

            if charge.category_id:
                phone['uniqname_correct'] = charge.uniqname_correct
                phone['uniqname'] = charge.uniqname
                phone['migrate'] = charge.migrate
                #phone['physical_phone_required'] = charge.physical_phone_required
                phone['notes'] = charge.notes
                phone['category'] = charge.category_id
                phone['other_category'] = charge.other_category
                phone['update_date'] = charge.update_date
                phone['updated_by'] = charge.updated_by

            subid = charge.subscriber_id

        if phone:
            phone_list.append(phone)

        return phone_list


class SelectionAbstract(models.Model):    

    MIGRATE_CHOICES = [
        ('YES', 'Yes'),
        ('NO', 'No'),
        ('NOT_YET', 'Not Yet'),
        ('CANCEL', 'Disconnect Line'),
    ]

    UNIQNAME_CHOICES = [  # Is the uniqname correct?
        ('YES', 'Yes'),
        ('CHANGE', 'No'),
        ('NA', 'Not Applicable'),
    ]

    ADD_UNIQNAME_CHOICES = [  # Is there a uniqname?
        ('CHANGE', 'Yes'),
        ('NA', 'Not Applicable'),
    ]

    subscriber = models.IntegerField(primary_key=True)
    uniqname_correct = models.CharField(max_length=12, choices=UNIQNAME_CHOICES)
    uniqname = models.CharField(max_length=8)
    migrate = models.CharField(max_length=12) #, choices=MIGRATE_CHOICES)
    location_correct = models.BooleanField(null=True)
    notes = models.TextField(max_length=200, blank=True, null=True)
    category = models.ForeignKey(Category, limit_choices_to={'sequence__isnull': False} ,on_delete=models.CASCADE)
    other_category = models.CharField(max_length=80, blank=True, null=True)
    update_date = models.DateTimeField(null=True)
    updated_by = models.CharField(null=True, max_length=8)
    service_id = models.IntegerField(null=True)
    service_number = models.CharField(max_length=60, null=True) 
    location_id = models.IntegerField(null=True)
    building_code = models.CharField(max_length=10, null=True)
    building = models.CharField(max_length=25, null=True)
    floor = models.CharField(max_length=18, null=True)
    room = models.CharField(max_length=18, null=True)
    jack = models.CharField(max_length=30, null=True)
    cable_path_id = models.IntegerField(null=True)

    objects = SelectionManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.uniqname

class Selection(SelectionAbstract):
    pass

    class Meta:
        db_table = 'PINN_CUSTOM\".\"um_softphone_selection'
        managed = False


class SelectionV(SelectionAbstract):
    dept_id = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)

    class Meta:
        db_table = 'PINN_CUSTOM\".\"um_softphone_selection_v'
        managed = False


class SubscriberCharges(SelectionAbstract):
    current_uniqname = models.CharField(max_length=8) 
    current_first_name = models.CharField(max_length=200) 
    current_last_name = models.CharField(max_length=200) 
    dept_id = models.CharField(max_length=10)
    subscriber_id = models.CharField(max_length=10)
    user_defined_id = models.CharField(max_length=10)
    building = models.CharField(max_length=10)
    floor = models.CharField(max_length=10)
    room = models.CharField(max_length=10)
    jack = models.CharField(max_length=10)
    location_since_date = models.CharField(max_length=10)
    #mrc_account = models.CharField(max_length=10)
    #item_code = models.CharField(max_length=10)
    #item_description = models.CharField(max_length=80)
    charges = models.JSONField()
    #quantity = models.CharField(max_length=10)
    #unit_price = models.FloatField(max_length=10)
    #charge_amount = models.CharField(max_length=10)
    #account = models.CharField(max_length=10)

    class Meta:
        db_table = 'PINN_CUSTOM\".\"um_softphone_v'
        managed = False


class DeptV(models.Model):
    dept_id = models.CharField(max_length=10, primary_key=True)
    dept_name = models.CharField(max_length=200)
    total = models.IntegerField()
    selections_made = models.IntegerField()
    remaining = models.IntegerField()

    class Meta:
        db_table = 'PINN_CUSTOM\".\"um_softphone_dept_v'
        managed = False