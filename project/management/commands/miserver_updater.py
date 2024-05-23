from django.core.management.base import BaseCommand, CommandError
from order.models import Server
import datetime, csv

class Command(BaseCommand):
    help = 'Change production values of miservers based off of csv file'

    def add_arguments(self, parser):
        parser.add_argument('filename',type=str)

    def handle(self, *args, **options):
        print(datetime.datetime.now(), 'start')
        filename = options['filename']
        print(f'Process {filename}')
        print('open file')

        with open(f'{filename}') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for row in csv_reader:
                server_name = ', '.join([item.strip() for item in row])
                print("processing", server_name)
                try:
                    server = Server.objects.get(name__iexact=server_name)
                    print(server.production)
                except Server.DoesNotExist:
                    print(f"No server found with name: {server_name}")