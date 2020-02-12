from django.core.management.base import BaseCommand, CommandError

from order.models import StorageInstance #, StorageHost, StorageMember, StorageRate
from project.pinnmodels import UmBillInputApiV

import datetime, csv

class Command(BaseCommand):
    help = 'Upload Billing daat for MiStorage to Pinnacle'

    def handle(self, *args, **options):
        print(datetime.datetime.now(), 'Upload File')

        today = datetime.datetime.now().strftime('%m%d%Y')
        x = 0

        instances = StorageInstance.objects.filter(pk=[4422, 4421, 4405, 4397, 3526, 3480, 3956, 4039, 4155, 4015])
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
            x =+1

        print(datetime.datetime.now(), x, 'Records Loaded')
