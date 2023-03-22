from django.db import models

class UmTollCallDetail(models.Model):
    billing_date = models.DateField(blank=True, null=True)
    deptid = models.CharField(max_length=30, blank=True, null=True)
    phone_number = models.CharField(max_length=60, blank=True, null=True)
    user_name = models.CharField(max_length=401, blank=True, null=True)
    user_defined_id = models.CharField(max_length=20, blank=True, null=True)
    subscriber_id = models.CharField(max_length=7, blank=True, null=True)
    chartcom = models.CharField(max_length=100, blank=True, null=True)
    service_type = models.CharField(max_length=100, blank=True, null=True)
    multiple_locations_flag = models.CharField(max_length=1, blank=True, null=True)
    building = models.CharField(max_length=36, blank=True, null=True)
    floor = models.CharField(max_length=18, blank=True, null=True)
    room = models.CharField(max_length=18, blank=True, null=True)
    jack = models.CharField(max_length=30, blank=True, null=True)
    connect_date = models.DateField(blank=True, null=True)
    display_connect_date = models.CharField(max_length=10, blank=True, null=True)
    display_connect_time = models.CharField(max_length=5, blank=True, null=True)
    usage_subtype_code = models.CharField(max_length=20)
    to_number = models.CharField(max_length=80, blank=True, null=True)
    from_number = models.CharField(max_length=80, blank=True, null=True)
    location = models.CharField(max_length=29, blank=True, null=True)
    call_classification = models.CharField(max_length=40, blank=True, null=True)
    call_description = models.CharField(max_length=25, blank=True, null=True)
    city = models.CharField(max_length=25, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    call_duration = models.FloatField(blank=True, null=True)
    dur_mn = models.FloatField(blank=True, null=True)
    dur_ss = models.FloatField(blank=True, null=True)
    amount_billed = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        managed = False
        unique_together = (('billing_date', 'deptid'))
        db_table = 'PINN_CUSTOM\".\"um_toll_call_detail_v'

class DownloadLog(models.Model):
    department_id = models.IntegerField()
    report_year = models.IntegerField()
    report_month = models.CharField(max_length=10)
    report_type = models.CharField(max_length=10)
    clicked_at = models.DateTimeField(auto_now_add=True)
    clicked_by = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.report_month} {self.report_year} - {self.department_id} {self.report_type}'