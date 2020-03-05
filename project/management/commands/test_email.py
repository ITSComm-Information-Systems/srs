from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group
from order.models import StorageInstance, StorageHost, StorageMember, Item

import datetime, csv

class Command(BaseCommand):
    help = 'Send Incident to SN'

    def add_arguments(self, parser):
        parser.add_argument('item_id',type=int)

    def handle(self, *args, **options):
        print(datetime.datetime.now(), 'Start')

        item_id = options['item_id']
        item=Item.objects.get(id=item_id)
        print(item.data)
        item.submit_incident()

        print(datetime.datetime.now(), 'End')
