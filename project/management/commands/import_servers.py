from django.core.management.base import BaseCommand, CommandError
from django.db.models.query_utils import Q

from oscauth.utils import get_mc_group
from oscauth.models import LDAPGroup
from order.models import Server, ServerDisk
from project.models import Choice


import datetime, csv, sys
import xml.etree.ElementTree as ET

OS = {
        'Red Hat Enterprise Linux 7 64-bit - Managed': 116, 
        'RedHatEnterpriseLinux764bitmanaged':116,
        'Red Hat Enterprise Linux 6 64-bit - Managed':113,
        'RedHatEnterpriseLinux664bitmanaged':113,
        'Windows2012R2managed':112,
        'Windows 2012 R2 - Managed':112,
        'Windows2016managed':5,
        'Windows 2016 - Managed':5,
        'Windows 2019 - Managed':4,
        'Windows2019managed':4,
        'Windows2008R2managed':111,
        'Windows 2008 R2 - Managed':111,
        'Ubuntu 16.04 LTS 64-bit - Managed':7,
        'Ubuntu1804LTS64bitManaged':7,
        'Ubuntu 18.04 LTS 64-bit - Managed':7,
        'Ubuntu1604LTS64bitManaged':7,
        'RedHatEnterpriseLinux564bitmanaged':115,
        'CentOS 4/5/6 (64-bit)':27,
        'CentOS 6 64-bit':27,
        'CentOS6':27,
        'CentOS664-bit':27,
        'Debian 6 64-bit':27,
        'Debian GNU/Linux 6 (64-bit)':27,
        'Debian664bit':27,
        'None':27,
        'Other Linux (64-bit)':27,
        'otherLinux2432bit':27,
        'otherLinux2664bit':27,
        'otherLinux64bit':27,
        'Oracle Linux 4/5/6 (64-bit)':27,
        'OracleLinux64bit':27,
        'RedHatEnterpriseLinux564bit':114,
        'Red Hat Enterprise Linux 6 64-bit':120,
        'RedHatEnterpriseLinux664bit':120,
        'Red Hat Enterprise Linux 7 (64-bit)':28,
        'RedHatEnterpriseLinux764bit':28,
        'SUSELinuxEnterpriseServer1164bit':27,
        'SUSELinuxEnterpriseServer1264bit':27,
        'Ubuntu 10 Linux 64-bit':27,
        'Ubuntu10Linux64bit':27,
        'Ubuntu 11 Linux 64-bit':27,
        'Ubuntu Linux (64-bit)':31,
        'UbuntuLinux64bit':27,
        'Microsoft Windows 8 (64-bit)':121,
        'WindowsServer2003':121,
        'Microsoft Windows Server 2008 (64-bit)':121,
        'Microsoft Windows Server 2008 R2 (64-bit)':121,
        'Windows Server 2008 64-bit':121,
        'Windows2008R2':121,
        'WindowsServer2008':121,
        'Microsoft Windows Server 2012 (64-bit)':34,
        'WindowsServer201264bit':34,
        'Microsoft Windows Server 2016 (64-bit)':35,
        'WindowsServer201664bit':35
    }


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

PATCH_DAY = {}
for choice in Choice.objects.filter(parent__code=('SERVER_PATCH_DATE')):
    PATCH_DAY[choice.label] = choice.id

REBOOT_DAY = {}
for choice in Choice.objects.filter(parent__code=('SERVER_REBOOT_DATE')):
    REBOOT_DAY[choice.label] = choice.id

ON_CALL_CHOICES = {}
for choice in Choice.objects.filter(parent__code=('ON_CALL_CHOICES')):
    ON_CALL_CHOICES[choice.code] = choice.id


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

        self.out_of_service_count = 0

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

            print(f'Out of Service Ignored {self.out_of_service_count}')
            print(f'Processed {line_count} lines.')
            print(f'Loaded {self.LOADS} lines.')
            print(f'Errors {self.ERRORS} lines.')

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
                print(len(disk_list), 'extra disks for server_id:', server_id, server_name)
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
                    size = int(tb * 1024)
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
                        print(val, 'checkbox not found')
                    

        return id_list



    def process_record(self, row, type, service_id):

        s = Server()

        mc_group =  row[1].strip("'")
        s.shortcode = row[3].strip("'")
        data = row[5].strip("'")
        server_name = row[6].strip("'")

        try:
            xml = ET.fromstring(data)
        except:
            print('error converting XML', server_name)
            return
        
        self.xml = xml

        service_status = self.get_text(xml, 'servicestatus', None)
        if service_status == 'Ended':
            self.out_of_service_count += 1
            return
        elif service_status == 'Active':
            s.in_service = True
        else:
            print('unknown service status', service_status, 'for', server_name)

        s.legacy_data = data
        s.owner = LDAPGroup().lookup( mc_group )
        s.admin_group = s.owner
        s.name = self.get_text(xml, 'name', 'Not Found')
        if self.get_text(xml, 'SRVmanaged', '') == 'Managed':
            s.managed = True
        else:
            s.managed = False

        os_name = self.get_text(xml, 'os', None)
        s.os_id = OS.get(os_name)

        #os = Choice.objects.filter(label=os_name)

        #if os:
        #    s.os = os[0]
        #else:
        #    os = Choice.objects.filter(code=os_name)
        #    if os:
        #        s.os = os[0]
        #    else:
        #        print('os not found', os_name)

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

        sub = self.get_text(xml, 'ipsubnet', '')
        if sub == 'public':
            s.public_facing = True
        else:
            s.public_facing = False

        s.created_date = self.get_text(xml, 'subscribedDate', None)

        s.backup_time_id = self.get_time('dailybackuptime', BACKUP_TIME, s.name)
        s.patch_time_id = self.get_time('patchingScheduleTime', PATCH_TIME, s.name)
        s.reboot_time_id = self.get_time('rebootScheduleTime', REBOOT_TIME, s.name)

        s.reboot_day_id = REBOOT_DAY.get(self.get_text(xml, 'rebootScheduleDate', None), None)
        s.patch_day_id = PATCH_DAY.get(self.get_text(xml, 'patchingScheduleDate', None), None)

        on_call = self.get_text(xml, 'monitoringsystem', None)
        if on_call == 'businesshours':
            s.on_call = ON_CALL_CHOICES['BUSINESS_HOURS']
        elif on_call == '247':
            s.on_call = ON_CALL_CHOICES['24/7']



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
            print('insert error', ex, server_name)
            self.ERRORS +=1

        #print(f'{self.LOADS} records Loaded, {self.ERRORS} errors')

    def get_time(self, field, map, name): # for a good time call 867-5309

        time = self.get_text(self.xml, field, None)
        if not time:
            return
        else:
            if time.startswith('0'):
                time = time[1:9]
            #print('time', time)
            #time = time.replace('0','').replace(':','')
            #print('time', time)
            id = map.get(time)
            if id:
                return id
            else:
                print(time, 'time not found for', field, name)
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
