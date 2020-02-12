from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group
from order.models import StorageInstance, StorageHost, StorageMember, StorageRate
from project.pinnmodels import UmBillInputApiV

import datetime, csv

class Command(BaseCommand):
    help = 'Upload Billing daat for MiStorage to Pinnacle'

    def add_arguments(self, parser):
        parser.add_argument('filename',type=str)

    def handle(self, *args, **options):
        print(datetime.datetime.now(), 'Upload File')

        instances = StorageInstance.objects.all()
        for instance in instances:
            print(instance, instance.rate.get_total_cost(instance.size))

            rec = UmBillInputApiV()
            rec.data_source = 'MiStorage'
            rec.assign_date = instance.created_date.strftime('%m%d%y')
            rec.unique_identifier = instance.name
            rec.short_code = instance.shortcode
            #rec.charge_identifier = 'TBD'
            rec.quantity_vouchered = instance.size
            rec.total_amount = instance.rate.get_total_cost(instance.size)
            rec.voucher_comment = instance.owner
            rec.save()
