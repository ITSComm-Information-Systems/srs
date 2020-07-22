from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group, McGroup
from order.models import BackupDomain, BackupNode, Item
from oscauth.models import LDAPGroup

#import datetime, csv

class Command(BaseCommand):
    help = 'Add Backup Domain'

    def add_arguments(self, parser):
        parser.add_argument('id',type=int)


    def handle(self, *args, **options):

        id = options['id']
        item = Item.objects.get(id=id)

        item.route()