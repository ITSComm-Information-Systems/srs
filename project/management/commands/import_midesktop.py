from django.core.management.base import BaseCommand, CommandError
from django.db.models.fields import NullBooleanField
from oscauth.utils import get_mc_group
from oscauth.models import LDAPGroup
from services.models import Network, Image, MiDesktop, Pool, ImageDisk
import datetime
import csv
import sys
import xml.etree.ElementTree as ET


class Command(BaseCommand):
    help = 'Import MiDesktop Images, Networks, Desktops ' \
        '"python3 manage.py import_midesktop Images" ' \
        'loads file from ~/Downloads/images.csv'

    def add_arguments(self, parser):
        parser.add_argument('model', type=str)
        parser.add_argument('number_of_records', nargs='?',
                            type=int, default=99999)

    def handle(self, *args, **options):
        print(datetime.datetime.now(), 'start')
        target = globals()[options['model']]
        filename = target.file
        number_of_records = options['number_of_records']
        print('open file')
        self.ERRORS = 0
        self.LOADS = 0
        with open(f'/Users/djamison/Downloads/{filename}', encoding='mac_roman') as csv_file:
            csv_reader = csv.reader(
                csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    # print(f'Column names are {", ".join(row)}')
                    line_count += 1
                elif line_count < number_of_records:
                    target.process_record(row)
                    line_count += 1
                else:
                    break
            print(f'Processed {line_count} lines.')
            print(f'errors {self.ERRORS} rec.')
            print(f'saved {self.LOADS} rec.')
        print(datetime.datetime.now(), 'end')


class Networks():
    file = 'networks.csv'

    def process_record(row):
        network = Network()
        network.name = row[0].strip("'")
        # network.vlan = row[1].strip("'")
        # network.network = row[2].strip("'")
        network.size = row[3].strip("'")
        network.owner = LDAPGroup().lookup(row[4].strip("'"))
        network.save()


class Images():
    file = 'images.csv'

    def process_record(row):
        # 0Base images    1GPU 2CPU 3RAM 4Storage 5Owner

        try:
            net = Network.objects.get(name=row[6].strip("'"))
        except:
            net = None
    
        image = Image()
        image.name = row[0].strip("'")
        image.gpu = row[1].strip("'").capitalize()
        image.cpu = row[2].strip("'")
        image.memory = row[3].strip("'")
        image.owner = LDAPGroup().lookup(row[5].strip("'"))
        image.network = net
        image.save()

        disk = ImageDisk()
        disk.image = image
        disk.name = 'disk0'
        disk.size = row[4].strip("'")
        disk.save()


class Pools():
    file = 'pools.csv'

    # 0Pool	1Shortcode	2Customer	3Image	4Network	5GPU	6Specs	7Pool qty

    def process_record(row):
        # Base images    GPU CPU RAM Storage Owner
        pool = Pool()
        pool.name = row[0].strip("'")
        pool.shortcode = row[1].strip("'")
        pool.owner = LDAPGroup().lookup(row[2].strip("'"))
        pool.quantity = row[7].strip("'")
        pool.save()

        images = Image.objects.filter(name=row[3].strip("'"))
        pool.images.set(images)
