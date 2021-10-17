from django.core.management.base import BaseCommand, CommandError

from order.models import ArcInstance

import datetime, json

BYTES_PER_TERABYTE = 1024 ** 4   # Base 2

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
        json_data = open(filename)   
        data = json.load(json_data) # deserialises it
        #data2 = json.dumps(data1) # json formatted string
        line_count = 0
        error_count = 0

        for record in data:
            line_count += 1
            amount_used = record['used'] / BYTES_PER_TERABYTE

            try:
                vol = ArcInstance.objects.get(id=record['id'])
                vol.amount_used = amount_used
                vol.research_computing_package = True
                vol.save()
            except Exception as e: 
                print(record['id'], e)
                error_count += 1






        json_data.close()



        print(f'Read {line_count} lines.')
        print(f'Errors {error_count}')

        print(datetime.datetime.now(), 'end')
