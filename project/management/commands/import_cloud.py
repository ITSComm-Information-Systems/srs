from django.core.management.base import BaseCommand, CommandError
from django.db.models.query_utils import Q

from oscauth.utils import get_mc_group
from oscauth.models import LDAPGroup
from project.models import Choice

from services.models import *

import datetime, csv, sys
import xml.etree.ElementTree as ET

VERSION_ID = {}
for choice in Choice.objects.filter(parent__code='AWS_VERSION'):
    VERSION_ID[choice.label] = choice.id


CHOICE_LIST = {}
# dt_acp, dt_cui, dt_ferpa, dt_fisma, dt_glba, dt_hsr, dt_itar, dt_itSecInfo, dt_otherData, dt_otherDataInfo, dt_pci, dt_phi, dt_pii, dt_snn
for choice in Choice.objects.filter(parent__code__in=('REGULATED_SENSITIVE_DATA','NON_REGULATED_SENSITIVE_DATA')):
    if choice.code == 'FERPA':
        CHOICE_LIST['dt_ferpa'] = choice.id
    elif choice.code == 'GLBA':
        CHOICE_LIST['dt_glba'] = choice.id
    elif choice.code == 'HSR':
        CHOICE_LIST['dt_hsr'] = choice.id
    #else:
    #    CHOICE_LIST[choice.code] = choice.id

class Record:
    pass

class Command(BaseCommand):
    help = 'Import CSV from Cloud Services'

    ERRORS = 0
    LOADS = 0

    def add_arguments(self, parser):
        parser.add_argument('filename',type=str)
        parser.add_argument('number_of_records', nargs='?', type=int, default=99999)

    def handle(self, *args, **options):
        print(datetime.datetime.now(), 'start')
        filename = options['filename']
        number_of_records = options['number_of_records']

        service = filename[:3].upper()
        print('service', service)

        print(f'Process {filename} {service}')

        model = globals()[service]
        model.objects.all().delete()
        
        print('open file')

        self.out_of_service_count = 0

        with open(f'/Users/djamison/Downloads/{filename}', encoding='mac_roman') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                #if line_count < 2:
                    heading = row
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                elif line_count < number_of_records:
                    record = Record()
                    for count, field in enumerate(row):
                        setattr(record, heading[count], field)

                    if service == 'AWS':
                        self.process_aws_record(record)
                    elif service == 'GCP':
                        self.process_gcp_record(record)

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


    def process_aws_record(self, record):
        instance = AWS()

        instance.account_id = record.awsAccountId
        instance.billing_contact = record.billingContact
        instance.shortcode = record.shortcode
        instance.requestor = record.requestor
        instance.created_date = record.dateCreated
        instance.data_classification = record.dataClassification
        instance.egress_waiver = self.to_boo(record.EgressWaiver)
        instance.owner = LDAPGroup().lookup( record.mcomm )
        instance.security_contact = record.securityContact
        instance.version_id = VERSION_ID[record.version]
        instance.vpn = self.to_boo(record.vpn)
        
        instance.save()

        instance.regulated_data.set( self.get_checkboxes(record) )
        #instance.non_regulated_data = record

        print('process', record.awsAccountId, record.dt_pii)


    def process_gcp_record(self, record):
        contact = record.billingContact.split('@')

        obj, created = GCP.objects.get_or_create(
            account_id = record.billingId,
            defaults={'billing_contact': contact[0], 'shortcode': record.shortcode},
        )

        instance = GCPProject()
        instance.account = obj 

        #instance.account_id = record.awsAccountId
        instance.billing_contact = record.billingContact
        instance.shortcode = record.shortcode
        instance.requestor = record.requestor
        instance.created_date = record.dateCreated
        #instance.data_classification = record.dataClassification
        #instance.regulated_data.set() = record
        #instance.non_regulated_data = record
        #instance.egress_waiver = self.to_boo(record.EgressWaiver)
        instance.owner = LDAPGroup().lookup( record.mcomm )
        instance.security_contact = record.securityContact
        #instance.version_id = VERSION_ID[record.version]
        instance.vpn = self.to_boo(record.vpn)
        
        instance.save()

        self.LOADS += 1

    def get_checkboxes(self, record):
        checkbox_list = []

        for key, value in CHOICE_LIST.items():
            if getattr(record, key) == 'True':
                checkbox_list.append(value)

        return checkbox_list