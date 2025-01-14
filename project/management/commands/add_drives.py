import csv
from django.core.management.base import BaseCommand
from order.models import Server, ServerDisk

class Command(BaseCommand):
    help = 'Add a 10GB disk to each server'

    def handle(self, *args, **kwargs):
        servers = """INSERT SERVER NAMES HERE
"""

        server_names = servers.split('\n')

        with open('server_drives_before.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Server Name'])

            for server_name in server_names:
                try:
                    server = Server.objects.get(name=server_name)
                    output_row =[server.name]

                    for drive in server.disks.all():
                        output_row.append([drive.name, drive.size])
                    writer.writerow(output_row)

                except Server.DoesNotExist:
                    pass
                    #print(f'Server with name "{server_name}" does not exist.')

        for server_name in server_names:
            try:
                server = Server.objects.get(name=server_name)
                self.stdout.write(f'Server found: {server.name}')

                drive_count = server.disks.count()
                self.stdout.write(f'The server currently has {drive_count} drive(s).')

                #display the drives
                for drive in server.disks.all():
                    self.stdout.write(f'Drive: {drive.name} - {drive.size}GB')

                new_disk = ServerDisk.objects.create(
                    server=server,
                    name='disk' + str(drive_count),
                    controller=0,
                    device=0,
                    size=10  # Size in GB
                )
                self.stdout.write(f'New disk created: {new_disk.name} with size {new_disk.size}GB')
            except Server.DoesNotExist:
                pass
                #self.stdout.write(f'Server with name "{server_name}" does not exist.')

        with open('server_drives_after.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Server Name'])

            for server_name in server_names:
                try:
                    server = Server.objects.get(name=server_name)
                    output_row =[server.name]

                    for drive in server.disks.all():
                        output_row.append([drive.name, drive.size])
                    writer.writerow(output_row)

                except Server.DoesNotExist:
                    pass
                    #print(f'Server with name "{server_name}" does not exist.')
            