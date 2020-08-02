from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group
from oscauth.models import LDAPGroup
from order.models import ArcInstance, ArcHost, StorageRate, ArcBilling

import datetime, csv

class Command(BaseCommand):
    help = 'Import CSV from MiStorage'

    def add_arguments(self, parser):
        parser.add_argument('filename',type=str)
        #parser.add_argument('type',type=str)
        #parser.add_argument('service_id',type=int)
        # turbo = 9, locker = 10

    def handle(self, *args, **options):
        print(datetime.datetime.now(), 'start')
        filename = options['filename']

        service_id = 11
        type = 'NFS'

        print(f'Process {filename} {service_id} {type}')
        ArcInstance.objects.filter(service_id=11,type=type).delete()
        
        print('open file')

        with open(f'/Users/djamison/Downloads/{filename}') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    #print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    self.process_record(row, type, service_id)
                    line_count += 1

            print(f'Processed {line_count} lines.')

        print(datetime.datetime.now(), 'end')

    def process_record(self, row, type, service_id):
        instance = ArcInstance()
        instance.uid = row[0]
        mc_group =  row[1].strip("'")
        instance.owner = LDAPGroup().lookup( mc_group )
        instance.nfs_group_id = row[2]
        instance.name = row[3].strip("'")
        instance.size = row[4]

        shortcode = row[5]
        instance.signer = [6]
        instance.rate_id = 28
        instance.service_id = 11

        #try:
        instance.save()
        print('saved instance')

        sc = ArcBilling()
        sc.size = instance.size
        sc.shortcode = shortcode
        sc.arc_instance_id = instance.id 
        sc.save()
        print('saved shortcode')

        #except:
        #    print('error', row[0], vars(instance))



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
