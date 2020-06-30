from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group
from oscauth.models import LDAPGroup
from order.models import ArcInstance, ArcHost, StorageRate

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

        if filename[:5] == 'turbo':
            service_id = 9
        else:
            service_id = 10

        if filename[-7:] == 'nfs.csv':
            type = 'NFS'
        else:
            type = 'CIFS'

        print(f'Process {filename} {service_id} {type}')
        #instance_list = ArcInstance.objects.filter(id)
        ArcHost.objects.filter(arc_instance__service_id=service_id,arc_instance__type=type).delete()
        ArcInstance.objects.filter(service_id=service_id,type=type).delete()
        
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
        instance.name = row[3].strip("'")
        #instance.owner = row[7].strip("'")
        mc_group =  row[7].strip("'")
        instance.owner = LDAPGroup().lookup( mc_group )
        
        instance.shortcode = row[8]
        instance.size = row[4]
        instance.created_date = row[5].strip("'")

        options = row[6].strip("'").strip("'")

        if type=='NFS':
            instance.type = 'NFS' 
            instance.uid = row[9]
            if row[10].strip("'") == 'Yes':
                instance.great_lakes = True
            if row[11].strip("'") == 'Yes':
                instance.sensitive_regulated = True

            
            if service_id == 9:  #Turbo
                if row[13].strip("'") == 'Yes':
                    instance.mutli_protocol = True
                instance.ad_group = row[14].strip("'")
                hosts = row[15].strip("'").split(' ')
            else:
                hosts = row[13].strip("'").split(' ')

            instance.nfs_group_id = row[12].strip("'")


        if type=='CIFS':
            instance.type = 'CIFS'
            hosts = None
            instance.ad_group = row[9].strip("'")
            if row[10].strip("'") == 'Yes':
                instance.sensitive_regulated = True

        instance.service_id = service_id
        instance.rate = StorageRate.objects.get(type=instance.type, service_id=service_id, label=options)


        try:
            instance.save()

            if hosts:
                for host in hosts:
                    h = ArcHost()
                    h.arc_instance = instance
                    h.name = host
                    h.save()
        except:
            print('error', row[0], vars(instance))




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
