from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group
from order.models import StorageInstance, StorageHost, StorageMember, StorageRate, StorageOwner

import datetime, csv

class Command(BaseCommand):
    help = 'Sync membership for StorageOwner groups with MCommunity'

    def handle(self, *args, **options):
        
        for owner in StorageOwner.objects.order_by('name'):

            mc = get_mc_group(owner.name)

            storage_members = StorageMember.objects.filter(storage_owner=)

            if mc:
                dn = mc.entry_dn[3:mc.entry_dn.find(',')]

                for member in mc['member']:
                    uid = member[4:member.find(',')]
                    print(uid)

            break


    