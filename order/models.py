from django.contrib.postgres.fields import JSONField
from django.db import models
from oscauth.models import Role
from project.pinnmodels import UmOscPreorderApiV
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.db import connections
import json
import cx_Oracle

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
        ('PhoneLocationForm', 'Phone Location'),
        ('EquipmentForm', 'Equipment'),
        ('NewLocationForm', 'New Location'),
        ('AddlInfoForm', 'Additional Information'),
        ('ReviewForm', 'Review'),
        ('ChartfieldForm', 'Chartfield'),
        ('RestrictionsForm', 'Restrictions'),
        ('FeaturesForm', 'Features'),
        ('StaticForm', 'Static Page'),
        ('AuthCodeForm', 'Auth Codes'),
        ('CMCCodeForm', 'CMC Codes'),
        ('ProductForm', 'Quantity Model'),

    )

    custom_form = models.CharField(blank=True, max_length=20, choices=FORM_CHOICES)


class Element(Configuration):
    ELEMENT_CHOICES = (
        ('', ''),
        ('Radio', 'Radio'),
        ('ST', 'String'),
        ('NU', 'Number'),
        ('Chart', 'Chartcom'),
        ('Label', 'Label'),
    )
    label = models.TextField()
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=ELEMENT_CHOICES)
    attributes = models.CharField(blank=True, max_length=1000)
    display_condition = models.CharField(blank=True, max_length=100)
    target = models.CharField(max_length=80, blank=True, null=True)


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
    name = models.CharField(max_length=20)
    label = models.CharField(max_length=100)
    display_seq_no = models.PositiveIntegerField()

    def __str__(self):
        return self.label
    
    class Meta:
        verbose_name_plural = "Feature Categories"


class FeatureType(models.Model):
    name = models.CharField(max_length=20)
    label = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.label

    
class Feature(Configuration):
    TYPE_CHOICES = (
        ('STD', 'Standard'),
        ('OPT', 'Optional'),
        ('SPD', 'Speed Call'),
        ('VM', 'Voice Mail'),
    )

    category = models.ManyToManyField(FeatureCategory)
    #type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    type = models.ForeignKey(FeatureType, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    additional_info = models.TextField(blank=True)
    active = models.BooleanField(default=True)


class Restriction(Configuration):
    category = models.ManyToManyField(FeatureCategory)


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
    cart_label = models.CharField(max_length=100, blank=True, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='A')
    description = models.TextField(blank=True, null=True)
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


class Chartcom(models.Model):
    fund = models.CharField(max_length=30)
    dept = models.CharField(max_length=30)
    program = models.CharField(max_length=30)
    class_code = models.CharField(max_length=30)
    project_grant = models.CharField(max_length=30)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.fund

    @property
    def account_number(self):
        account_number = self.fund + '-' + self.dept + '-' + self.program + '-' + self.class_code
        if self.project_grant:
            account_number = account_number + '-' + self.project_grant

        return account_number

    def get_user_chartcoms(self):
        chartcom_list = UserChartcomV.objects.filter(user=self).order_by('name')
        user_chartcoms = []
        
        for chartcom in chartcom_list:
            user_chartcoms.append((chartcom.chartcom_id, chartcom.name, chartcom.dept))

        return user_chartcoms

    def get_user_chartcom_depts(self):
        dept_list = UserChartcomV.objects.filter(user=self).order_by('dept').distinct('dept')
        user_chartcom_depts = []
        
        for chartcom in dept_list:
            user_chartcom_depts.append((chartcom.dept))

        return user_chartcom_depts

class UserChartcomV(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    chartcom = models.ForeignKey(Chartcom, on_delete=models.PROTECT)
    name = models.CharField(max_length=20, blank=True, primary_key=True)
    dept = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'order_user_chartcom'


class LogItem(models.Model):
    transaction = models.CharField(max_length=20)
    local_key = models.CharField(max_length=20, blank=True)
    remote_key = models.CharField(max_length=20, blank=True)
    create_date = models.DateTimeField('Date Created', auto_now_add=True)
    level = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)

    def add_log_entry(self, local_key, descr):
        self.transaction = 'Create Issue'
        self.local_key = local_key
        self.remote_key = 23432
        self.level = 'Info'
        self.description = descr
        self.save()
    

class Order(models.Model):
    order_reference = models.CharField(max_length=20)
    create_date = models.DateTimeField('Date Created', auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    chartcom = models.ForeignKey(Chartcom, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)

    @property
    def dept(self):
        return self.chartcom.dept

    def create_preorder(self):
        data =  {  
                    "department_number": self.chartcom.dept,
                    "default_one_time_expense_acct": self.chartcom.account_number,
                    "submitter": self.created_by.username,
                }

        item_list = Item.objects.filter(order_id=self.id)
        elements = Element.objects.exclude(target__isnull=True).exclude(target__exact='')
        map = {}

        for element in elements:
            map[element.name] = element.target

        equipment_only = True

        for num, item in enumerate(item_list, start=1):
            issue = {}
            if num == 1:
                #data['priority_name'] = 'High'
                #data['due_date'] = '01/20/2019'
                data['issues'] = []

            action_id = item.data['action_id']
            action = Action.objects.get(id=action_id)
            if action.type != 'E':
                equipment_only = False

            cons = Constant.objects.filter(action=action_id)
            for con in cons:  # Populate issue with constants
                issue[con.field] = con.value

            note = item.data['reviewSummary'] + 'CHARTCOM \nOCC:' + item.chartcom.account_number + '\n'

            for key, value in item.data.items():
                if value:  # Populate issue with user supplied values
                    if key == 'MRC' or key == 'localCharges' or key == 'LD':
                        value = Chartcom.objects.get(id=value).account_number
                        note = note + key+ ':' + value + '\n'

                    target = map.get(key)
                    if target != None:
                        issue[target] = value

            issue['add_info_text_3'] = self.id

            issue['note'] = note #item.data['reviewSummary']
            issue['comment_text'] = item.description
            data['issues'].append(issue)

        if equipment_only:
            data['equipment_only'] = 'Y'

        json_data = json.dumps({"Order": data})

        LogItem().add_log_entry(item.id, json_data)
        #log.add_log_entry(json_data)

        with connections['pinnacle'].cursor() as cursor:
            ponum = cursor.callfunc('um_osc_util_k.um_add_preorder_f', cx_Oracle.STRING , [json_data])
            print(ponum)

        LogItem().add_log_entry(item.id, ponum)

        self.order_reference = ponum
        self.save()


class Item(models.Model):
    description = models.CharField(max_length=100)
    create_date = models.DateTimeField('Date Created', auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    deptid = models.CharField(max_length=8)
    chartcom = models.ForeignKey(Chartcom, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    data = JSONField()

    def __str__(self):
        return self.description

    @property
    def days_to_deletion(self):
        delete_date = self.create_date + timedelta(days=180) 
        days_to_deletion = delete_date - timezone.now()
        return days_to_deletion.days

    def leppard(self):
        pour=['me']
        pour.append('sugar')