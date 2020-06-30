from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group
from oscauth.models import LDAPGroup
from order.models import BackupDomain, BackupNode

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

        print(f'Process {filename}')

        
        print('open file')

        with open(f'/Users/djamison/Downloads/{filename}') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            line_count = 0
            domain = ''
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                    
                else:
                    if domain != row[0]:
                        bd = self.process_record(row)

                    domain = row[0]

                    if bd:
                        node = BackupNode()
                        node.backup_domain = bd
                        node.name = row[7]
                        node.time = row[8]
                        #node.notes
                        node.save()

                    line_count += 1

            print(f'Processed {line_count} lines.')

        print(datetime.datetime.now(), 'end')

    def process_record(self, row):
        bd = BackupDomain()
        bd.name = row[0]
        bd.shortcode = row[2]
        bd.total_cost = 0
        #bd.owner_id = row[1]
        bd.owner = LDAPGroup().lookup( row[1] )
        bd.days_extra_versions = row[3]
        bd.days_only_version = row[4]
        bd.versions_after_deleted = row[5]
        bd.versions_while_exists = row[6]
        #bd.cost_calcluated_date = row[3]
        #bd.notes = row[9]

        try:
            bd.save()
            return bd
        except:
            print('err')


