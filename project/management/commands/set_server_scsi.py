from django.core.management.base import BaseCommand
from order.models import ServerDisk

import datetime

class Command(BaseCommand):
    help = 'One time run to set new fields controller/device'


    def handle(self, *args, **options):
        print(datetime.datetime.now(), 'start')
        line_count = 0

        for disk in ServerDisk.objects.all():
            line_count +=1 
            disk.controller = None
            disk.device = None
            disk.set_scsi_id()
            #print(disk, disk.id, disk.server_id)
            disk.save()
            #print('   ',disk.name, f'scsi-{disk.controller}:{disk.device}')

        print(f'Processed {line_count} records.')
        print(datetime.datetime.now(), 'end')
