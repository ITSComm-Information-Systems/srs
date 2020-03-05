from django.core.management.base import BaseCommand, CommandError

from order.models import StorageInstance #, StorageHost, StorageMember, StorageRate
from project.pinnmodels import UmBillInputApiV
from django.db import connections

from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Upload Billing daat for MiStorage to Pinnacle'

    def handle(self, *args, **options):
        print(datetime.now(), 'Upload Records')

        today = datetime.now().strftime('%m%d%Y')
        today = int(today)
        x = 0

        instances = StorageInstance.objects.filter(pk__gt=4710, pk__lt=4715)
        for instance in instances:
            print(instance, instance.rate.get_total_cost(instance.size))

            rec = UmBillInputApiV()
            rec.data_source = 'MiStorage'
            rec.assign_date = instance.created_date.strftime('%m%d%Y')
            rec.unique_identifier = instance.name
            rec.short_code = instance.shortcode
            rec.charge_identifier = instance.rate.name
            rec.quantity_vouchered = instance.size
            rec.total_amount = instance.rate.get_total_cost(instance.size)
            rec.voucher_comment = instance.owner
            rec.bill_input_file_id = today
            rec.save()
            x+=1

        print(datetime.now(), x, 'Records Loaded')

        print(datetime.now(), 'Load Infrastructure Billing')

        with connections['pinnacle'].cursor() as cursor:
            result = cursor.callproc('pinn_custom.um_util_k.um_scheduler_p',  ['JOBID21000', 'Load Infrastructure Billings'
                                   , (datetime.now() + timedelta(minutes=5)).strftime('%d-%b-%y %H:%M'),f"'MiStorage',{today}"] )
        
        print(datetime.now(), result)
        #print(datetime.now(), 'Update Expense Code')

        #with connections['pinnacle'].cursor() as cursor:
        #    result = cursor.callproc('pinn_custom.um_util_k.um_scheduler_p',  ['JOBID21002', 'Update Expense Subcode'
        #                          , (datetime.now() + timedelta(minutes=15)).strftime('%d-%b-%y %H:%M'), 'MiStorage'] )

        #print(datetime.now(), result)
        print(datetime.now(), 'Process Complete')