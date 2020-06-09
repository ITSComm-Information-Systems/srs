from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group, McGroup
from order.models import BackupDomain, BackupNode
from oscauth.models import LDAPGroup

#import datetime, csv

class Command(BaseCommand):
    help = 'Add Backup Domain'

    def handle(self, *args, **options):
        gname = 'iTSComm InformatioN systems'


        lg = LDAPGroup.objects.get(id=36)
        lg.update_membership()
        return


        bd = BackupDomain()
        bd.name = 'temp'
        bd.owner = LDAPGroup().lookup(gname)
        bd.short_code = '32423'
        bd.total_cost = 0
        bd.save()

    