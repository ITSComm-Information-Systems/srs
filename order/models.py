from django.contrib.postgres.fields import JSONField
from django.db import models
from oscauth.models import Role
from project.pinnmodels import UmOscPreorderApiV
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.db import connections

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

    )

    custom_form = models.CharField(blank=True, max_length=20, choices=FORM_CHOICES)


class Element(Configuration):
    ELEMENT_CHOICES = (
        ('', ''),
        ('Radio', 'Radio'),
        ('ST', 'String'),
        ('NU', 'Number'),
        ('Chart', 'Chartcom'),
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
        api = UmOscPreorderApiV()
        api.category_code = 2
        api.wo_type_code = 'WB'
        api.wo_type_category_id = 0
        api.action_name = 'Add'
        api.add_info_text_3 = self.id
        api.save()

        preorder = UmOscPreorderApiV.objects.get(add_info_text_3=self.id)

        self.order_reference = preorder.pre_order_number
        self.save()

        item_list = Item.objects.filter(order_id=self.id)

        elements = Element.objects.exclude(target__isnull=True).exclude(target__exact='')
        map = {}

        for element in elements:
            map[element.name] = element.target

        for num, item in enumerate(item_list, start=1):
            item.create_issue(preorder.pre_order_number, map)

        preorder = UmOscPreorderApiV.objects.filter(add_info_text_3=self.id, work_status_name=None)
        preorder.update(work_status_name = 'Received')


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

    def create_issue(self, preorder_number, map):
        api = UmOscPreorderApiV()
        api.add_info_text_3 = self.order_id
        api.add_info_text_4 = self.id
        action_id = self.data['action_id']
        api.pre_order_number = preorder_number

        cons = Constant.objects.filter(action=action_id)
        for con in cons:  # Populate the model with constants
            setattr(api, con.field, con.value)

        for key, value in self.data.items():
            if value:  # Populate the model with user supplied values
                if key == 'MRC' or key == 'localCharges' or key == 'LD':
                    value = Chartcom.objects.get(id=value).account_number

                target = map.get(key)
                if target != None:
                    setattr(api, target, value)

        api.comment_text = self.description
        api.default_one_time_expense_acct = self.chartcom.account_number

        try:
            api.save()
            log = LogItem()
            log.transaction = 'Create Issue'
            log.local_key = self.id
            log.remote_key = preorder_number
            log.level = 'Info'
            log.description = 'Preorder Created'
            log.save()

            with connections['pinnacle'].cursor() as cursor:
                id = UmOscPreorderApiV.objects.get(add_info_text_4=self.id).pre_order_id
                cursor.callproc('um_note_procedures_k.um_add_wo_tcom_note_p', [id, 'Order Details', self.data['reviewSummary'], ''])

        except Exception as e:
            log = LogItem()
            log.transaction = 'Create Issue'
            log.local_key = self.id
            log.remote_key = preorder_number
            log.level = 'Error'
            log.description = e
            log.save()
            print(e.with_traceback)

    def leppard(self):
        pour=['me']
        pour.append('sugar')