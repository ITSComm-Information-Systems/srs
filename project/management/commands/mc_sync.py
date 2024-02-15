from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group
from oscauth.models import LDAPGroup


import datetime, csv

class Command(BaseCommand):
    help = 'Sync membership for StorageOwner groups with MCommunity'

    def add_arguments(self, parser):
        parser.add_argument('--group')

    def handle(self, *args, **options):

        if options['group']:
            group  = LDAPGroup.objects.get(name=options['group'])
            group.update_membership()
            return

        # Update LDAP Group membership used by storage, etc.
        for group in LDAPGroup.objects.order_by('name'):
            try:
                group.update_membership()
            except:
                print('error updating group:', group)



