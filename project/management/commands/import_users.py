from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

import datetime, csv

class Command(BaseCommand):
    help = 'Import Users from CSV to Group'

    def add_arguments(self, parser):
        parser.add_argument('filename',type=str)


    def handle(self, *args, **options):
        print(datetime.datetime.now(), 'start')
        filename = options['filename']

        print(f'Process {filename}')

        
        print('open file')

        with open(f'/Users/djamison/Downloads/{filename}') as csv_file:
            group = Group.objects.get(name='Ambassador of Softphones')
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            line_count = 0
            not_found = 0
            domain = ''
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                    
                else:
                    line_count += 1
                    try:
                        u = User.objects.get(username=row[0])
                        u.groups.add(group)
                    except User.DoesNotExist:
                        print(row[0], 'not found')
                        not_found += 1

            print(f'Processed {line_count} lines.')

        print(datetime.datetime.now(), 'end')
