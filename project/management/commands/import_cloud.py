from django.core.management.base import BaseCommand, CommandError
from django.db.models.query_utils import Q

from oscauth.utils import get_mc_group
from oscauth.models import LDAPGroup
from order.models import Server, ServerDisk
from project.models import Choice

from services.models import AWSAccount

import datetime, csv, sys
import xml.etree.ElementTree as ET

VERSION_ID = {}
for choice in Choice.objects.filter(parent__code='AWS_VERSION'):
    VERSION_ID[choice.label] = choice.id


CHOICE_LIST = {}
# dt_acp, dt_cui, dt_ferpa, dt_fisma, dt_glba, dt_hsr, dt_itar, dt_itSecInfo, dt_otherData, dt_otherDataInfo, dt_pci, dt_phi, dt_pii, dt_snn
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

class Record:
    pass

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
                    heading = row
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                elif line_count < number_of_records:
                    record = Record()
                    for count, field in enumerate(row):
                        setattr(record, heading[count], field)

                    self.process_record(record)
                    line_count += 1
                else:
                    break

            print(f'Out of Service Ignored {self.out_of_service_count}')
            print(f'Processed {line_count} lines.')
            print(f'Loaded {self.LOADS} lines.')
            print(f'Errors {self.ERRORS} lines.')

        print(datetime.datetime.now(), 'end')

    def to_boo(self, val):
        val = val.upper()

        if val == 'YES' or val == 'TRUE':
            return True

        return False


    def process_record(self, record):


        instance = AWSAccount()

        instance.account_id = record.awsAccountId
        instance.billing_contact = record.billingContact
        instance.shortcode = record.shortcode
        instance.requestor = record.requestor
        instance.created_date = record.dateCreated
        instance.data_classification = record.dataClassification
        #instance.regulated_data = record
        #instance.non_regulated_data = record
        instance.egress_waiver = self.to_boo(record.EgressWaiver)
        instance.owner = LDAPGroup().lookup( record.mcomm )
        instance.security_contact = record.securityContact
        instance.version_id = VERSION_ID[record.version]
        instance.vpn = self.to_boo(record.vpn)
        
        instance.save()

        print('process', record.awsAccountId, record.dt_pii)

