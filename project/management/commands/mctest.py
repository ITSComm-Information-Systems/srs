from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group
from order.models import StorageInstance, StorageHost, StorageMember, StorageRate, StorageOwner

import datetime, csv

class Command(BaseCommand):
    help = 'Import CSV from MiStorage'

    def handle(self, *args, **options):
        
        last_owner = '-'

        for instance in StorageInstance.objects.order_by('owner_name'):

            print(instance.owner_name)
            if instance.owner_name != last_owner:
                mc = get_mc_group(instance.owner_name)
                last_owner = instance.owner_name

            if mc:
                dn = mc.entry_dn[3:mc.entry_dn.find(',')]

                try:
                    so = StorageOwner.objects.get(name=dn)
                except: #Make it so
                    so = StorageOwner()
                    so.name = dn
                    so.save()

                    for member in mc['member']:
                        uid = member[4:member.find(',')]
                        print(uid)
                        sm = StorageMember()
                        sm.storage_owner = so
                        sm.username = uid
                        sm.save()

                instance.owner_id = so
                instance.save()

    