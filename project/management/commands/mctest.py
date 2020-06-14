from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group, McGroup
from order.models import BackupDomain, BackupNode, Item
from oscauth.models import LDAPGroup

#import datetime, csv

class Command(BaseCommand):
    help = 'Add Backup Domain'

    def handle(self, *args, **options):
        gname = 'iTSComm InformatioN systems'

        i = Item.objects.get(id=3107)
        i.route()
    