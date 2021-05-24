from django.core.management.base import BaseCommand, CommandError
from django.db.models.fields import NullBooleanField

from oscauth.utils import get_mc_group
from oscauth.models import LDAPGroup
from order.models import Database, Server, ServerDisk

from project.models import Choice

import datetime, csv, sys
import xml.etree.ElementTree as ET

DAYS = {
        'Sunday': 0,
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6
}

class Command(BaseCommand):
    help = 'Import CSV from MiDatabase'



    def add_arguments(self, parser):
        parser.add_argument('filename',type=str)
        parser.add_argument('number_of_records', nargs='?', type=int, default=99999)


    def handle(self, *args, **options):
        print(datetime.datetime.now(), 'start')
        filename = options['filename']
        number_of_records = options['number_of_records']

        service_id = 11
        type = 'NFS'

        print(f'Process {filename} {service_id} {type}')
        Database.objects.all().delete()
        
        print('open file')

        self.database_types = {}
        for choice in Choice.objects.filter(parent__code='DATABASE_TYPE'):
            self.database_types[choice.code] = choice.id

        self.database_versions = {}
        for choice in Choice.objects.filter(parent__code='DATABASE_VERSION'):
            if choice.code == 'SQL2017':
                self.database_versions['2017SQL'] = choice.id
            elif choice.code == 'SQL2019':
                self.database_versions['2019SQL'] = choice.id
            else:
                self.database_versions[choice.code] = choice.id

        print(self.database_versions)

        self.ERRORS = 0
        self.LOADS = 0

        with open(f'/Users/djamison/Downloads/{filename}', encoding='mac_roman') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    #print(f'Column names are {", ".join(row)}')
                    line_count += 1
                elif line_count < number_of_records:
                    self.process_record(row, type, service_id)
                    line_count += 1
                else:
                    break

            print(f'Processed {line_count} lines.')
            print(f'errors {self.ERRORS} rec.')
            print(f'saved {self.LOADS} rec.')

        print(datetime.datetime.now(), 'end')

    def get_text(self, xml, key, default):

        try:
            value = xml.find(key).text
            if value:
                return value
            else:
                return default 
        except:
            return default

    def add_disks(self, xml, server_id):
        disks = self.get_text(xml, 'diskspace', None)

        if not disks:
            return
        
        disk_list = disks.split(';')

        for disk in disk_list:
            if len(disk_list) > 9:
                print('extra disks', server_id)
                sys.exit()

            if disk:
                equal = disk.find('=')
                space = disk.find(' ')
                name = disk[0:equal]
                size = int(disk[equal+1:space])

                sd = ServerDisk()
                sd.server_id = server_id
                sd.name = name
                sd.size = size
                sd.save()

    def add_data(self, xml, server):
        x = self.get_text(xml, 'MWregulateddatacheckboxe1', None)
        if x:
            print(x)

        x = self.get_text(xml, 'nonregulateddataDetail', None)
        if x:
            print(x)

    def process_record(self, row, type, service_id):

        d = Database()

        mc_group =  row[1].strip("'")
        d.shortcode = row[3].strip("'")
        data = row[5].strip("'")

        try:
            xml = ET.fromstring(data)
        except:
            print('error converting XML', data)
            return
    

        service_status = self.get_text(xml, 'servicestatus', None)
        if service_status == 'Ended':
            return
            #d.in_service = False
        elif service_status == 'Active':
            d.in_service = True
        else:
            d.service_status = None
            print('service status', service_status)

    
        size = self.get_text(xml, 'MDDBSize', None)
        if size:
            size = size.replace('GB','')
            size = int(size)
            d.size = size


        d.legacy_data = data
        d.name = self.get_text(xml, 'xmlSubscriptionKey', None)   #instancename?
        d.owner = LDAPGroup().lookup( mc_group )
        d.support_email = self.get_text(xml, 'afterhoursemail', 'n/a')
        d.support_phone = self.get_text(xml, 'afterhoursphone', 'n/a')
        #d.cpu = self.get_text(xml, 'cpu', 0)
        #d.ram = self.get_text(xml, 'ram', 0)

        d.url = self.get_text(xml, 'databaseURL', None)

        on_call = self.get_text(xml, 'monitoringsystem', None)
        if on_call == 'businesshours':
            d.on_call = 0
        elif on_call == '247':
            d.on_call = 1
        else:
            print('warning on_call ', on_call, 'not found')



        d.purpose = self.get_text(xml, 'databasepurpose', '')


        if self.get_text(xml, 'MDsharedordedicated', None) == 'dedicated':
            try:
                d.server = Server.objects.get(name=d.name)
            except:
                print('Server not found', d.name)

        type = self.get_text(xml, 'MDDBType', None)
        if type:
            d.type_id = self.database_types.get(type.upper())

        try:
            d.save()
            self.LOADS +=1
            #self.add_disks(xml, d.id)
            #self.add_data(xml)
        except Exception as ex:
            print('insert error', ex)
            print(data)
            self.ERRORS +=1

        #print(f'{self.LOADS} records Loaded, {self.ERRORS} errors')


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
