from django.core.management.base import BaseCommand, CommandError
from django.db.models.query_utils import Q

from oscauth.utils import get_mc_group
from oscauth.models import LDAPGroup
from order.models import Server, ServerDisk
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

CHOICE_LIST = {}

for choice in Choice.objects.filter(parent__code__in=('REGULATED_SENSITIVE_DATA','NON_REGULATED_SENSITIVE_DATA')):
    if choice.code == 'HIPAA':
        CHOICE_LIST['PHI'] = choice.id
    elif choice.code == 'OTHERREG':
        CHOICE_LIST['ORS'] = choice.id
    elif choice.code == 'FERPA':
        CHOICE_LIST['SER'] = choice.id
    elif choice.code == 'TRADESEC':
        CHOICE_LIST['TSI'] = choice.id
    elif choice.code == 'ITSEC':
        CHOICE_LIST['ITS'] = choice.id
    elif choice.code == 'ECR':
        CHOICE_LIST['EXS'] = choice.id
    elif choice.code == 'AUDIT':
        CHOICE_LIST['INT'] = choice.id
    elif choice.code == 'OTHERNONREG':
        CHOICE_LIST['ONRN'] = choice.id
    elif choice.code == 'GLBA':
        CHOICE_LIST['SLA'] = choice.id  #Student Load Information
    else:
        CHOICE_LIST[choice.code] = choice.id

print(CHOICE_LIST)

BACKUP_TIME = {}
for choice in Choice.objects.filter(parent__code=('SERVER_BACKUP_TIME')):
    BACKUP_TIME[choice.label] = choice.id

print('x', BACKUP_TIME)

PATCH_TIME = {}
for choice in Choice.objects.filter(parent__code=('SERVER_PATCH_TIME')):
    PATCH_TIME[choice.label] = choice.id

REBOOT_TIME = {}
for choice in Choice.objects.filter(parent__code=('SERVER_REBOOT_TIME')):
    REBOOT_TIME[choice.label] = choice.id


class Command(BaseCommand):
    help = 'Import CSV from MiServer'

    ERRORS = 0
    LOADS = 0

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
        Server.objects.all().delete()
        
        print('open file')

        with open(f'/Users/djamison/Downloads/{filename}', encoding='mac_roman') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                #sif line_count < 68:
                    #print(f'Column names are {", ".join(row)}')
                    line_count += 1
                elif line_count < number_of_records:
                    self.process_record(row, type, service_id)
                    line_count += 1
                else:
                    break

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

    def add_disks(self, xml, server_id):
        disks = self.get_text(xml, 'diskspace', None)

        if not disks:
            return
        
        disk_list = disks.split(';')

        for disk in disk_list:
            if len(disk_list) > 9:
                print(len(disk_list), 'extra disks for server_id:', server_id)
                return
                
            if disk:
                equal = disk.find('=')
                space = disk.find(' ')
                name = disk[0:equal]
                uom = disk[space+1:space+3]

                if uom == 'GB':
                    size = int(disk[equal+1:space])
                elif uom == 'TB':
                    tb = float(disk[equal+1:space])
                    size = int(tb * 1000)
                else:
                    print('error in disk unit', uom)
                    return

                sd = ServerDisk()
                sd.server_id = server_id
                sd.name = name
                sd.size = size
                sd.save()

    def get_checkboxes(self, xml, field):
        id_list = []
        x = self.get_text(xml, field, None)
        if x and x != '[]':
            x = x.replace('[', '')
            x = x.replace(']', '')
            x = x.replace(' ', '')

            val_list = x.split(',')
            for val in val_list:
                if val:
                    if CHOICE_LIST.get(val):
                        id_list.append(CHOICE_LIST.get(val))
                    else:
                        print(val, 'not found')
                    

        return id_list



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
        
        self.xml = xml

        s.legacy_data = data
        s.owner = LDAPGroup().lookup( mc_group )
        s.name = self.get_text(xml, 'name', 'Not Found')
        if self.get_text(xml, 'SRVmanaged', '') == 'Managed':
            s.managed = True
        else:
            s.managed = False
        s.os = self.get_text(xml, 'os', 'n/a')
        s.cpu = self.get_text(xml, 'cpu', 0)
        s.ram = self.get_text(xml, 'ram', 0)
        #s.disk_space = self.get_text(xml, 'diskspace', '')
        s.firewall = ' ' 
        s.support_email = self.get_text(xml, 'afterhoursemail', 'n/a')
        s.support_phone = self.get_text(xml, 'afterhoursphone', 'n/a')
        if self.get_text(xml, 'diskBackup', '') == 'Yes':
            s.backup = True
        else:
            s.backup = False
            
        if self.get_text(xml, 'diskBackup', '') == 'Yes':
            s.backup = True
        else:
            s.backup = False

        if self.get_text(xml, 'replicated', '') == 'Yes':
            s.replicated = True
        else:
            s.replicated = False


        #sbu = self.get_time('dailybackuptime', BACKUP_TIME)

        s.backup_time_id = self.get_time('dailybackuptime', BACKUP_TIME, s.name)
        s.patch_time_id = self.get_time('patchingScheduleTime', PATCH_TIME, s.name)
        s.reboot_time_id = self.get_time('rebootScheduleTime', REBOOT_TIME, s.name)
        s#._time_id = self.get_time('dailybackuptime', BACKUP_TIME)
        #s.patch_time = PATCH_TIME.get(self.get_text(xml, 'patchingScheduleTime', None))
        #s.reboot_time = REBOOT_TIME.get(self.get_text(xml, 'rebootScheduleTime', None))
        s.reboot_day = DAYS.get(self.get_text(xml, 'rebootScheduleTime', None), None)

        on_call = self.get_text(xml, 'monitoringsystem', None)
        if on_call == 'businesshours':
            s.on_call = 0
        elif on_call == '247':
            s.on_call = 1

        service_status = self.get_text(xml, 'servicestatus', None)
        if service_status == 'Ended':
            s.in_service = False
        elif service_status == 'Active':
            s.in_service = True
        else:
            print('unknown service status', service_status)

        try:
            s.save()
            self.LOADS +=1
            self.add_disks(xml, s.id)
            #self.add_data(xml)
            reg_list = self.get_checkboxes(xml, 'MWregulateddatacheckboxe1')
            if len(reg_list) > 0:
                s.regulated_data.set(reg_list)

            nonreg_list = self.get_checkboxes(xml, 'nonregulateddataDetail')
            if len(nonreg_list) > 0:
                s.non_regulated_data.set(nonreg_list)

        except Exception as ex:
            print('insert error', ex)
            print(data)
            self.ERRORS +=1

        #print(f'{self.LOADS} records Loaded, {self.ERRORS} errors')

    def get_time(self, field, map, name): # for a good time call 867-5309

        time = self.get_text(self.xml, field, None)
        if not time:
            return
        else:
            time = time.replace('0','').replace(':','')
            id = map.get(time)
            if id:
                return id
            else:
                print(time, 'not found for', field, name)
                return None



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
