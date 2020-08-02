from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group
from oscauth.models import LDAPGroup


import datetime, csv

class Command(BaseCommand):
    help = 'Sync membership for StorageOwner groups with MCommunity'

    def handle(self, *args, **options):

        # Update LDAP Group membership used by storage, etc.
        for group in LDAPGroup.objects.order_by('name'):
            print('update', group)
            group.update_membership()