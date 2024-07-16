from django.core.management.base import BaseCommand
from django.conf import settings
from cryptography.fernet import Fernet
from project.models import Unity

import datetime, csv

class Command(BaseCommand):
    help = 'Import CSV'

    def handle(self, *args, **options):

        print(datetime.datetime.now(), 'start')

        fernet = Fernet(settings.UNITY_KEY)
        print('open file')

        with open(f'/Users/djamison/Downloads/unity.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    #print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    temp_pass = row[1]
                    pass_hash = fernet.encrypt(temp_pass.encode())
                    Unity.objects.create(username=row[0]
                                         , temp_password=pass_hash.decode()
                                         , temp_pin=row[2]
                                         , phone_number=row[3])
                    line_count += 1

            print(f'Processed {line_count} lines.')

        print(datetime.datetime.now(), 'end')

def decode():

    fernet = Fernet(settings.UNITY_KEY)
    for user in Unity.objects.all():
        pwd = fernet.decrypt(user.temp_password.encode('ascii'))
        print(user.username, pwd.decode())
