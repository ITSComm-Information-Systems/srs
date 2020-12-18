from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group
from oscauth.models import LDAPGroup
from order.models import Server

import datetime, csv
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
    help = 'Import CSV from MiServer'

    ERRORS = 0
    LOADS = 0

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
        Server.objects.all().delete()
        
        print('open file')

        with open(f'/Users/djamison/Downloads/{filename}', encoding='mac_roman') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    #print(f'Column names are {", ".join(row)}')
                    line_count += 1
                elif line_count > 1180:
                    self.process_record(row, type, service_id)
                    line_count += 1
                else:
                    line_count += 1

            print(f'Processed {line_count} lines.')

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




    def process_record(self, row, type, service_id):

        s = Server()

        mc_group =  row[1].strip("'")
        s.shortcode = row[3].strip("'")
        data = row[5].strip("'")

        try:
            xml = ET.fromstring(data)
        except:
            print('error converting XML', data)
            return
    
        s.legacy_data = data
        s.owner = LDAPGroup().lookup( mc_group )
        s.name = self.get_text(xml, 'name', None)
        s.managed = self.get_text(xml, 'managed', False)
        s.os = self.get_text(xml, 'os', 'n/a')
        s.cpu = self.get_text(xml, 'cpu', 0)
        s.ram = self.get_text(xml, 'ram', 0)
        s.disk_space = self.get_text(xml, 'diskspace', '')
        s.firewall = ' ' 
        s.support_email = self.get_text(xml, 'afterhoursemail', 'n/a')
        s.support_phone = self.get_text(xml, 'afterhoursphone', 'n/a')
        s.backup_time = self.get_text(xml, 'dailybackuptime', None)
        s.patch_time = self.get_text(xml, 'patchingScheduleTime', None)
        s.reboot_time = self.get_text(xml, 'rebootScheduleTime', None)
        s.reboot_day = DAYS.get(self.get_text(xml, 'rebootScheduleTime', None), None)

        on_call = self.get_text(xml, 'monitoringsystem', None)
        if on_call == 'businesshours':
            s.on_call = 0
        elif on_call == '247':
            s.on_call = 1

        x = self.get_text(xml, 'MWregulateddatacheckboxe1', None)
        if x:
            print(x)

        x = self.get_text(xml, 'nonregulateddataDetail', None)
        if x:
            print(x)

        try:
            s.save()
            self.LOADS +=1
        except Exception as ex:
            print('insert error', ex)
            print(data)
            self.ERRORS +=1

        print(f'{self.LOADS} records Loaded, {self.ERRORS} errors')


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
