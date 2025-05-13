from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from project.pinnmodels import UmOscPreorderApiV, UmOscNoteProfileV
from datetime import datetime
from decimal import Decimal
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class BOM(models.Model):
    create_date = models.DateTimeField(null=True)
    created_by = models.CharField(null=True, max_length=32)
    update_date = models.DateTimeField(null=True)
    updated_by = models.CharField(null=True, max_length=32)

    class Meta:
        abstract = True

    def set_create_audit_fields(self, username):
        self.create_date = datetime.now()
        self.update_date = datetime.now()
        self.created_by = username
        self.updated_by = username

    def set_update_audit_fields(self, username):
        self.update_date = datetime.now()
        self.updated_by = username

    #class Meta
    #def __str__()
    #def save()
    #def get_absolute_url()
    #Any custom methods

class LegacyData(BOM):
    sys_id = models.CharField(max_length=32, primary_key=True)
    parent_sys_id = models.CharField(null=True,max_length=32)
    record_name = models.CharField(max_length=32)
    new_record_id = models.IntegerField(null=True)
    multi = models.IntegerField(null=True)
    woid = models.IntegerField(null=True)
    status = models.CharField(max_length=20)
    commodity_id = models.IntegerField(null=True)
    commodity_code = models.CharField(null=True, max_length=32)
    commodity_descr = models.CharField(null=True, max_length=200)
    hours = models.DecimalField(null=True, max_digits=8, decimal_places=2)
    quantity = models.IntegerField(null=True)
    price = models.DecimalField(null=True, max_digits=8, decimal_places=2)
    contingency_amount = models.DecimalField(null=True, max_digits=8, decimal_places=2)
    contingency_percentage = models.DecimalField(null=True, max_digits=8, decimal_places=2)
    location_name = models.CharField(null=True, max_length=200)
    location_descr = models.CharField(null=True, max_length=1000)
    assigned_engineer = models.IntegerField(null=True)
    addl_1 = models.CharField(null=True, max_length=200)
    addl_2 = models.CharField(null=True, max_length=200)
    data = models.TextField()

    vendor = models.CharField(max_length=50, default='')
    reel_number = models.CharField(max_length=20, default='')
    staged = models.BooleanField(default=False)
    order_date = models.DateField(null=True, blank=True)
    estimated_receive_date = models.DateField(null=True, blank=True)
    release_number = models.CharField(max_length=50, default='')

    class Meta: 
        db_table = 'um_bom_legacy_data'
    

class Technician(models.Model):
    ACTIVE = 1
    INACTIVE = 0

    labor_id = models.IntegerField(primary_key=True)
    labor_code = models.CharField(max_length=20)
    labor_name_display = models.CharField(max_length=80)
    user_name = models.CharField(max_length=80)
    active = models.PositiveSmallIntegerField()
    wo_group_code = models.CharField(max_length=32)

    class Meta:
        db_table = 'um_bom_technician_v'
        managed = False

    def __str__(self):
        return self.labor_name_display
        

class Workorder(models.Model):
    pre_order_id = models.IntegerField(primary_key=True)
    wo_number_display = models.CharField(max_length=20)
    pre_order_number = models.IntegerField()
    project_display = models.CharField(max_length=200)
    status_name = models.CharField(max_length=10)
    comment_text = models.TextField()
    building_number = models.IntegerField(blank=True, null=True)
    building_name = models.CharField(max_length=100)
    multi_count = models.IntegerField()
    estimate_id = models.IntegerField()

    class Meta: 
        db_table = 'um_bom_search_v'
        managed = False

    def __str__(self):
        return self.wo_number_display


class PreOrder(models.Model):
    pre_order_id = models.IntegerField(primary_key=True)
    wo_number_display = models.CharField(max_length=50)
    pre_order_number = models.IntegerField()
    status_name = models.CharField(max_length=50)
    project_display = models.CharField(max_length=50)
    project_code_display = models.CharField(max_length=50)
    add_info_list_value_name_2 = models.CharField(max_length=50)
    add_info_list_value_code_2 = models.CharField(max_length=50)
    due_date = models.DateTimeField(null=True, blank=True)
    actual_fulfilled_date = models.DateTimeField(null=True, blank=True)
    estimated_start_date = models.DateTimeField(null=True, blank=True)
    estimated_completion_date = models.DateTimeField(null=True, blank=True)
    add_info_list_value_name_1 = models.CharField(max_length=50)
    add_info_list_value_code_1 = models.CharField(max_length=50)
    department_name = models.CharField(max_length=50)
    form_display_contact_name = models.CharField(max_length=50)
    contact_phone_number = models.CharField(max_length=50)
    contact_email_address = models.CharField(max_length=50)
    comment_text = models.CharField(max_length=200)
    assigned_labor_name_display = models.CharField(max_length=200)

    add_info_checkbox_1 = models.BooleanField(null=True, verbose_name="Draft Comp-D")
    add_info_checkbox_2 = models.BooleanField(null=True, verbose_name="Asbuilt Recv'd-D")
    add_info_checkbox_3 = models.BooleanField(null=True, verbose_name="Asbuilt Compl-D")
    add_info_checkbox_4 = models.BooleanField(null=True)
    add_info_checkbox_5 = models.BooleanField(null=True, verbose_name="Asbuilt/Prints-F")
    add_info_checkbox_6 = models.BooleanField(null=True, verbose_name="Closeout Compl-F")
    add_info_checkbox_7 = models.BooleanField(null=True, verbose_name="Asbuilt/Prints Received-A")
    add_info_checkbox_8 = models.BooleanField(null=True, verbose_name="Assignments Complete-A")

    class Meta: 
        db_table = 'um_bom_preorder_v'
        managed = False

    def __str__(self):
        return self.wo_number_display


class EstimateManager(models.Manager):
    def assigned_to(self, username):

        sql = '''
            select *
            from um_bom_estimate_search_v est 
            where (status_name = 'Open'
                    and status = 'Estimate' 
                    and assigned_engineer = %s
                    and engineer_status = 'NOT_COMPLETE' 
                    and not exists (select 'x' from um_bom_estimate_search_v 
                                    where pre_order_number = est.pre_order_number 
                                    and (engineer_status <> 'NOT_COMPLETE' or status <> 'Estimate')) )
            or
                    (assigned_netops = %s
                    and pre_order_number in (select pre_order_number from um_bom_project_v where status > 1) )
            or 
                    (status_name = 'Open' 
                    and status <> 'Rejected' 
                    and project_manager = %s)
            or
                    (status_name = 'Open' 
                    and status in ('Approved' , 'Ordered', 'Warehouse') 
                    and engineer_status = 'NOT_COMPLETE' 
                    and assigned_engineer = %s)
        '''

        return self.raw(sql, [username,username,username,username])
    

class EstimateView(models.Model):
    OPEN = ['Estimate', 'Warehouse', 'Ordered', 'Approved']
    ENGINEER_STATUS = [
        ('COMPLETE', 'Complete'),
        ('NOT_COMPLETE', 'Not Complete'),
    ]
    objects = EstimateManager()

    id = models.IntegerField(primary_key=True)
    label = models.IntegerField()
    status = models.CharField(max_length=20)
    status_name = models.CharField(max_length=20)
    #created_by = models.CharField(max_length=20)
    wo_number_display = models.CharField(max_length=20)
    pre_order_number = models.IntegerField()
    project_display = models.CharField(max_length=200)
    project_manager = models.CharField(max_length=20)
    assigned_engineer = models.CharField(max_length=20)
    assigned_netops = models.CharField(max_length=20)
    due_date = models.DateTimeField(null=True, blank=True)
    estimated_start_date = models.DateTimeField(null=True, blank=True)
    actual_fulfilled_date = models.DateTimeField(null=True, blank=True)
    estimated_completion_date = models.DateTimeField(null=True, blank=True)
    engineer_status = models.CharField(max_length=20, choices=ENGINEER_STATUS, default='NOT_COMPLETE')

    class Meta: 
        db_table = 'um_bom_estimate_search_v'
        managed = False

    def __str__(self):
        return self.wo_number_display


class Estimate(BOM):
    REJECTED = 0
    ESTIMATE = 1
    WAREHOUSE = 2
    ORDERED = 3
    COMPLETED = 4
    CANCELLED = 5
    APPROVED = 6

    STATUS_CHOICES = [
        (REJECTED, 'Rejected'),
        (ESTIMATE, 'Estimate'),
        (APPROVED, 'Approved'),
        (WAREHOUSE, 'Warehouse'),
        (ORDERED, 'Ordered'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    ENGINEER_STATUS = [
        ('COMPLETE', 'Complete'),
        ('NOT_COMPLETE', 'Not Complete'),
    ]

    woid = models.IntegerField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=ESTIMATE)
    label = models.CharField(max_length=20)
    assigned_engineer = models.ForeignKey(Technician, on_delete=models.CASCADE, blank=True,null=True)
    engineer_status = models.CharField(max_length=20, choices=ENGINEER_STATUS, default='NOT_COMPLETE')
    contingency_amount = models.DecimalField(null=True, max_digits=8, decimal_places=2, default=0)
    contingency_percentage = models.IntegerField(null=True, default=0)
    folder = models.URLField(null=True, blank=True)
    legacy_data = models.TextField(null=True)
    legacy_id = models.CharField(max_length=32, default=0)

    @property
    def read_only(self):
        if self.status:
            if int(self.status) in [self.ESTIMATE, self.WAREHOUSE, self.ORDERED, self.APPROVED]:
                return False
            else:
                return True
        else:
            return True

    class Meta: 
        db_table = 'um_bom_estimate'

        permissions = (
                ('can_access_bom', 'Base Access - Add, View & Create Estimates'),
                ('can_update_bom_ordered', 'Warehouse - Update Material after estimate stage')
        )

    def __str__(self):
        return self.label

    #def get_absolute_url(self):

    def __init__(self, *args, **kwargs):
        super(Estimate, self).__init__(*args, **kwargs)
        self.initial_status = self.status
        self.initial_engineer_status = self.engineer_status

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.

        if self.initial_engineer_status == 'NOT_COMPLETE' and self.engineer_status == 'COMPLETE':
            self.get_workorder()  # TODO make these properties.
            email_list = [f'{self.workorder.add_info_list_value_code_2}@umich.edu']
            Notification.objects.send_email('BOM Engineer Work Complete', self, email_list)

        if self.status != self.initial_status:
            Notification.objects.notify(self)

            if self.initial_status != self.APPROVED and self.status == self.APPROVED:
                Estimate.objects.filter(woid=self.woid,status=self.ESTIMATE).update(status=self.REJECTED)
                Estimate.objects.filter(id=self.id).update(engineer_status='NOT_COMPLETE')

    def import_material_from_csv(self, file, user):

        result = []
        inserts = 0
        errors = 0

        for line in file:  #TODO base field location on headings
            fields = line.decode('utf-8').split(',')
            location = fields[0].strip()
            item_code = fields[1].strip().upper()
            quantity = fields[2].strip()

            mat = Material()
            mat.set_create_audit_fields(user.username)
            new_location = MaterialLocation.objects.get_or_create(estimate=self, name=location)
            mat.material_location = new_location[0]
            mat.quantity = quantity
            mat.item_code = item_code

            try:
                mat.save()
                result.append(f'{item_code} Imported')
                inserts += 1
            except:
                result.append(f'*****Error: {item_code} not found*****')
                errors += 1
        
        result.append(f'{inserts} inserted, {errors} errors')

        return result

    def get_detail(self):
        #self.workorder = Workorder.objects.get(pre_order_id=self.woid)
        self.get_workorder()
        self.get_project()

        self.note_list = UmOscNoteProfileV.objects.filter(note_keyid_value=self.woid).order_by('-note_id')
 
        self.list = Estimate.objects.filter(woid=self.woid).order_by('create_date')

        self.material_list = self.get_material()
        self.material_total = 0
        for item in self.material_list:
            self.material_total = self.material_total + item.extended_price

        self.part_list = Material.objects.filter(material_location__estimate=self).order_by('item').values('item','item__code','item__name','item__manufacturer_part_number','item__price','release_number','reel_number','staged','status','price').annotate(Sum('quantity'))

        self.location_list = MaterialLocation.objects.filter(estimate_id=self.id).order_by('name')


        self.labor_list = Labor.objects.filter(estimate=self)
        self.labor_total = 0
        self.labor_hours = 0
        for item in self.labor_list:
            self.labor_total = self.labor_total + item.extended_cost
            self.labor_hours = self.labor_hours + item.hours

        labmat = self.labor_total + self.material_total

        if self.contingency_percentage:
            pct = Decimal(self.contingency_percentage) / 100
            self.contingency_total = round(labmat * pct,2)
        elif self.contingency_amount:
            self.contingency_total = self.contingency_amount
        else:
            self.contingency_total = 0

        self.total = labmat + self.contingency_total

    def get_workorder(self):
        try:
            self.workorder = PreOrder.objects.get(pre_order_id=self.woid)
        except PreOrder.DoesNotExist:
            self.workorder = None 

    def get_project(self):
        try:
            self.project = Project.objects.get(woid=self.woid)
            self.project.status_display = self.project.get_status_display()
        except Project.DoesNotExist:
            self.project = None

    def get_material(self):
        return Material.objects.filter(material_location__estimate=self).order_by('material_location__name').select_related()

    def get_labor(self):
        return Labor.objects.filter(estimate=self)

    def notify_warehouse(self):
        if self.status == self.ESTIMATE or self.status == self.ORDERED or self.status == self.APPROVED:
            self.status = self.WAREHOUSE
            self.save()
        elif self.status == self.WAREHOUSE:
            self.get_workorder()
            NotificationManager().send_email('BOM - Notify Warehouse', self, ['itcom.warehouse@umich.edu'])


class Project(BOM):
    COMPLETE = 1
    OPEN = 2
    IN_PROGRESS = 4
    STATUS_CHOICES = [
        (COMPLETE, 'Complete'),
        (OPEN, 'Open'),
        (IN_PROGRESS, 'In Progress'),
    ]

    woid = models.IntegerField()
    netops_engineer = models.ForeignKey(Technician,on_delete=models.CASCADE,blank=True,null=True, verbose_name='NetOps')
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, null=True)
    assigned_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    activity = models.TextField(default='')
    legacy_parent_id = models.CharField(max_length=32, default=0)

    class Meta: 
        db_table = 'um_bom_project'

    def notify_engineer(self, estimate_id):
        estimate = Estimate.objects.get(id=estimate_id)
        estimate.get_workorder()
        addr = f'{self.netops_engineer.user_name}@umich.edu'
        print(f'send to: {addr}')
        NotificationManager().send_email('Project assigned to you', estimate, [addr])


class ProjectView(BOM):

    COMPLETE = 1
    OPEN = 2
    REWORK = 3
    STATUS_CHOICES = [
        (COMPLETE, 'Complete'),
        (OPEN, 'Open'),
        (REWORK, 'Rework'),
    ]

    wo_number_display = models.CharField(max_length=14)
    pre_order_number = models.IntegerField()
    id = models.IntegerField(primary_key=True)
    create_date = models.DateTimeField(null=True)
    created_by = models.CharField(null=True, max_length=32)
    update_date = models.DateTimeField(null=True)
    updated_by = models.CharField(null=True, max_length=32)
    woid = models.IntegerField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, null=True)
    assigned_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    #activity = models.TextField(default='')
    legacy_parent_id = models.CharField(max_length=32, default=0)
    netops_engineer = models.ForeignKey(Technician,on_delete=models.CASCADE,blank=True,null=True, verbose_name='NetOps')
    estimate_id = models.IntegerField()
    status_name = models.CharField(max_length=60)
    project_display = models.CharField(max_length = 255, null=True)

    class Meta:
        db_table = 'um_bom_project_v'
        managed = False



class ItemManager(models.Manager):

    def get_active(self):
        return Item.objects.exclude(class_code='OU').exclude(class_code='T') 


class Item(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=12)
    name = models.CharField(max_length=50)
    class_code = models.CharField(max_length=2)
    subclass_name = models.CharField(max_length=20)
    manufacturer = models.CharField(max_length=50)
    manufacturer_part_number = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8,decimal_places=2)

    objects = ItemManager()

    def __str__(self):
        return f'{self.code} - {self.name}'

    class Meta:
        managed = False
        db_table = 'um_bom_item_v'


class MaterialLocation(BOM):
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    description = models.TextField(null=True)

    class Meta:
        db_table = 'um_bom_material_location'

    def __str__(self):
        return self.name


class Material(BOM):
    ESTIMATE = 1
    IN_STOCK = 2
    ORDERED = 3
    STATUS_CHOICES = [
        (ESTIMATE, 'Estimate'),
        (IN_STOCK, 'In Stock'),
        (ORDERED, 'Ordered'),
    ]
    MATERIAL_GIRL = True

    material_location = models.ForeignKey(MaterialLocation, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True) 
    item_code = models.CharField(max_length=20)
    item_description = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=50)
    manufacturer_part_number = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=ESTIMATE)

    vendor = models.CharField(max_length=50, default='', blank=True)
    reel_number = models.CharField(max_length=20, default='', blank=True)
    staged = models.BooleanField(default=False)
    order_date = models.DateField(null=True, blank=True)
    estimated_receive_date = models.DateField(null=True, blank=True)
    release_number = models.CharField(max_length=50, default='', blank=True)

    @property
    def extended_price(self):
        return self.quantity * self.price

    class Meta: 
        db_table = 'um_bom_material'

    def __str__(self):
        if self.item_code:
            return self.item_code
        else:
            return self.item_description

    def save(self, *args, **kwargs):
        if self.quantity == 0:
            self.delete()
            # Delete Locaiton if no children
            if Material.objects.filter(material_location_id=self.material_location.id).count() == 0:
                MaterialLocation.objects.get(id=self.material_location.id).delete()
            return

        if self.pk is None: # Set item info for new record
            if self.item_code:
                self.set_item_fields(self.item_code)
            else:
                self.item_code = 'New'

        super().save(*args, **kwargs)  # Call the "real" save() method.

    def set_item_fields(self, item_code):  # Capture item info at point in time it was added to BOM
        item = Item.objects.get(code=item_code)
        self.item_id = item.id
        self.price = item.price
        self.item_description = item.name
        self.manufacturer = item.manufacturer
        self.manufacturer_part_number = item.manufacturer_part_number


class LaborGroup(models.Model):
    id = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=20)
    rate_1 = models.CharField(max_length=80)
    rate_2 = models.CharField(max_length=80)

    class Meta: 
        db_table = 'um_bom_labor_group_v'
        managed = False

    def __str__(self):
        return self.name


class Labor(BOM):
    STANDARD = 1
    OVERTIME = 2
    FLAT = 3
    RATE_TYPE_CHOICES = [
        (STANDARD, 'Standard'),
        (OVERTIME, 'Overtime'),
        #(FLAT, 'Flat'),
    ]

    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE) 
    description = models.CharField(max_length=200, blank=True, default='')
    group = models.ForeignKey(LaborGroup, on_delete=models.CASCADE) 
    rate_type = models.PositiveSmallIntegerField(choices=RATE_TYPE_CHOICES, default=STANDARD)
    hours = models.DecimalField(max_digits=8, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def extended_cost(self):
        return round(self.hours * self.rate, 2)

    class Meta: 
        db_table = 'um_bom_labor'

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        if self.rate_type == self.STANDARD:
            self.rate = self.group.rate_1 
        if self.rate_type == self.OVERTIME:
            self.rate = self.group.rate_2

        super().save(*args, **kwargs)  # Call the "real" save() method.


class NotificationManager(models.Manager):

    def notify(self, estimate):
        estimate.get_project()
        estimate.get_workorder()

        if estimate.status in [estimate.ORDERED, estimate.WAREHOUSE]:
            note = UmOscNoteProfileV()
            note.note_type_code = 'Work Order'
            note.note_types_code = 'NOTE'
            note.note_subject = f'BOM {estimate.get_status_display()}'
            note.note_body = f'BOM: {estimate.label} ({estimate.id})'
            note.note_author = 'BOM'
            note.note_keyid_value = estimate.woid
            note.save()

        notification_list = self.filter(event=estimate.status)

        if len(notification_list) == 0:
            return

        email_list = []
        for notification in notification_list:
            if notification.recipient == 'project_manager':
                addr = f'{estimate.workorder.add_info_list_value_code_2}@umich.edu'
                print(f'send to: {addr}')
                email_list.append(addr)
            else:
                email_list.append(notification.recipient)

        self.send_email(str(notification), estimate, email_list)
  
    def send_email(self, subject, estimate, email_list):
        if settings.ENVIRONMENT == 'Production':
            environment = ''
            distribution = []
        else:
            environment = settings.ENVIRONMENT + ' - '
            distribution = email_list
            email_list = ['its-infrastructure-bom@umich.edu'] # Let's not spam from dev/qa

        if subject in Notification.NOTE_SUBJECTS: 
            note_list = UmOscNoteProfileV.objects.filter(note_keyid_value=estimate.woid,note_subject=subject).order_by('-note_id')
        else:
            note_list = []

        base_url = settings.SITE_URL
        msg_html = render_to_string('bom/email.html', {'estimate': estimate, 'base_url': base_url, 'note_list': note_list, 'distribution': distribution})
        subject = f'{environment}{subject} for {estimate.workorder.wo_number_display } Preorder: {estimate.workorder.pre_order_number}'
        message = 'BOM'
        send_mail(
            subject,
            message, 
            'its-infrastructure-bom@umich.edu', # From 
            email_list,
            fail_silently=True,
            html_message=msg_html,
        )


class PreDefinedNote(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    subject = models.CharField(max_length=80)

    class Meta:
        db_table = 'um_bom_predefined_note_v'
        managed = False


class Notification(models.Model):

    WAREHOUSE = 'BOM - Notify Warehouse (Send Email)'
    ROUTE_PM = 'BOM - Route to Project Manager (Send Email)'
    ORDERED = 'BOM - Material Ordered (Send Email)'

    NOTE_SUBJECTS = [WAREHOUSE, ROUTE_PM, ORDERED]
 
    EVENT_CHOICES = [
        (Estimate.ESTIMATE, 'BOM Created'),
        (Estimate.WAREHOUSE, WAREHOUSE),
        (Estimate.ORDERED, ORDERED),
        (Estimate.COMPLETED, 'BOM Completed'),
        (Estimate.CANCELLED, 'BOM Cancelled'),
        (Estimate.REJECTED, 'BOM Rejected'),
        (11, 'NetOps Created'),
        (12, ROUTE_PM)
    ]

    event = models.PositiveSmallIntegerField(choices=EVENT_CHOICES)
    recipient = models.CharField(max_length=80)
    objects = NotificationManager()

    def __str__(self): 
        return self.get_event_display()

    class Meta: 
        db_table = 'um_bom_notification'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self): 
        return self.item.name

    class Meta: 
        db_table = 'um_bom_favorites'

class ItemBarcode(models.Model):
    commodity_code = models.CharField(max_length=32)
    commodity_name = models.CharField(max_length=200)
    manufacturer_part_nbr = models.CharField(max_length=50)
    min_reorder_lvl = models.IntegerField()
    warehouse_code = models.CharField(max_length=32)
    warehouse_name = models.CharField(max_length=200)

    def __str__(self): 
        return self.commodity_code

    class Meta: 
        db_table = 'srs_bar_code_labels_v'