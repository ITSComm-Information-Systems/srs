from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group
from order.models import StorageInstance, StorageHost, StorageMember, StorageRate

import datetime, csv

class Command(BaseCommand):
    help = 'Import CSV from MiStorage'

    def add_arguments(self, parser):
        parser.add_argument('filename',type=str)

    def handle(self, *args, **options):
        #print(datetime.datetime.now(), 'Add Members')
        #self.add_members()
        #return

        print(datetime.datetime.now(), 'start')
        filename = options['filename']

        with open(f'/Users/djamison/Downloads/{filename}') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    #print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    self.process_record(row)
                    line_count += 1

            print(f'Processed {line_count} lines.')

        print(datetime.datetime.now(), 'Add Members')
        self.add_members()

        print(datetime.datetime.now(), 'end')

    def process_record(self, row):
        instance = StorageInstance()
        instance.name = row[3].strip("'")
        instance.owner = row[7].strip("'")
        instance.shortcode = row[8]
        instance.size = row[4]
        instance.created_date = row[5].strip("'")

        options = row[6].strip("'")

        if row[2] == 'nfs_storage':
            instance.type = 'NFS' 
            instance.uid = row[9]
            hosts = row[11].strip("'").split(' ')
            #if row[10] == 'on':
            #    options.append('flux')

        if row[2] == 'cifs_storage':
            instance.type = 'CIFS'
            hosts = None
            instance.deptid = row[9]

        instance.rate = StorageRate.objects.get(type=instance.type, label=options)

        instance.save()

        if hosts:
            for host in hosts:
                h = StorageHost()
                h.storage_instance = instance
                h.name = host
                h.save()

    def add_members(self):
        groups = StorageInstance.objects.distinct('owner')

        for group in groups:  # Loop through distinct groups
            members = get_mc_group(group.owner)  # Pull member list from MCommunity
            print(group.owner)
            if not members == None:
                usernames = []
                for member in members['member']:
                    usernames.append(member[4:member.find(',', 0, 99)])
                    #print('add', members['member'])

                usernames = list( dict.fromkeys(usernames) )
                
                
                instance_list = StorageInstance.objects.filter(owner=group.owner)
                for instance in instance_list:  # Add members to all instances using that MC group
                    print(instance)
                    for username in usernames:
                        print('      ', username)
                        sm = StorageMember()
                        sm.storage_instance = instance
                        sm.username = username
                        sm.save()
