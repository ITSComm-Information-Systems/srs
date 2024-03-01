from django.core.management.base import BaseCommand
from project.utils import get_query_result
from project.models import Email
import json, csv
from django.conf import settings

class Command(BaseCommand):
    help = 'Send email regarding retired softphone users.'

    def handle(self, *args, **options):
        print('Get Email')

        email = Email.objects.get(code='SOFTPHONE_RETIREES')

        with open('/media/final_email.csv', encoding='mac_roman') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for row in csv_reader:
                email.to = row[0] + '@umich.edu'
                email.context = {"phone_list": row[2].split(',') }
                email.send()





