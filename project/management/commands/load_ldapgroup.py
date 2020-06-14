from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group, McGroup
from order.models import BackupDomain, BackupNode, Item, StorageInstance
from oscauth.models import LDAPGroup

#import datetime, csv

class Command(BaseCommand):
    help = 'Add Backup Domain'

    def handle(self, *args, **options):
        gname = 'iTSComm InformatioN systems'

        instances = StorageInstance.objects.all()

        for instance in instances:
            print(instance.owner_bak.name)
            if get_mc_group(instance.owner_bak.name):
                instance.owner = LDAPGroup().lookup( instance.owner_bak.name ) 
                instance.save()
