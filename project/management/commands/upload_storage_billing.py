from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from django.core.mail import send_mail
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
        total_cost = 0

        instances = StorageInstance.objects.all()
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
            total_cost = total_cost + rec.total_amount
            rec.voucher_comment = instance.owner
            rec.bill_input_file_id = today
            rec.save()
            x+=1

            break

        print(datetime.now(), x, 'Records Loaded')
        print(datetime.now(), total_cost, 'Total Cost')

        body = f'Records Loaded: {x} \nTotal Cost: {total_cost}'

        print(datetime.now(), 'Load Infrastructure Billing')

        with connections['pinnacle'].cursor() as cursor:
            result = cursor.callproc('pinn_custom.um_util_k.um_scheduler_p',  ['JOBID21000', 'Load Infrastructure Billings'
                                   , (datetime.now() + timedelta(minutes=5)).strftime('%d-%b-%y %H:%M'),f"'MiStorage',{today}"] )
        
        send_mail('MiStorage Billing Records Uploaded', body, 'srs-otto@umich.edu', ['itscomm.information.systems@umich.edu'])
        print(datetime.now(), 'Process Complete')

