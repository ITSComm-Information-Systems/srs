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
        bd = BackupDomain.objects.get(id=id)
        print(bd)

        node = BackupNode.objects.get_or_create(backup_domain_id=id, name='louie', time='9:30 PM')
        print(node)
        
    