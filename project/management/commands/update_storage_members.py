from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group
from order.models import StorageInstance, StorageHost, StorageMember, StorageRate

import datetime, csv

class Command(BaseCommand):
    help = 'Daily user update from MCommunity for MiStorage'

    def handle(self, *args, **options):
        print(datetime.datetime.now(), 'start')

        print(datetime.datetime.now(), 'Update Members')
        self.update_members()

        print(datetime.datetime.now(), 'end')

    def update_members(self):
        groups = StorageInstance.objects.values('owner_name').distinct()

        all_users = []
        for group in groups:  # Loop through distinct groups
            members = get_mc_group(group.owner_name)  # Pull member list from MCommunity
            print(group.owner_name)
            if not members == None:
                usernames = []
                for member in members['member']:
                    usernames.append(member[4:member.find(',', 0, 99)])

                usernames = list( dict.fromkeys(usernames) )
                all_users = all_users + usernames
                
                instance_list = StorageInstance.objects.filter(owner_name=group.owner_name)
                for instance in instance_list:  # Add members to all instances using that MC group
                    print(instance)
                    for username in usernames:
                        print('      ', username)
                        exists = StorageMember.objects.filter(username=username)

                        # Create new member
                        if not exists:
                            sm = StorageMember()

                        # Update existing member
                        else:
                            sm = exists[0]

                        sm.storage_owner = instance.get_owner_instance(name=group.owner_name)
                        sm.username = username
                        sm.save()

        # Deal with member who needs to be deleted
        print('Delete members')
        members = StorageMember.objects.all()
        for member in members:
            if member.username not in all_users:
                print('member: {}'.format(member.username))
                member.delete()