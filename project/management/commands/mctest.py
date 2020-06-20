from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group, McGroup
from order.models import BackupDomain, BackupNode, Item
from oscauth.models import LDAPGroup

#import datetime, csv

class Command(BaseCommand):
    help = 'Add Backup Domain'

    def add_arguments(self, parser):
        parser.add_argument('item_id',type=int)


    def handle(self, *args, **options):

        item_id = options['item_id']
        i = Item.objects.get(id=3333)
        i.route()
    