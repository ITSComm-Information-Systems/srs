from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from project.models import Email
from softphone.models import SelectionV
import csv

class Command(BaseCommand):
    help = 'Send Email to Softphone Users'

    def add_arguments(self, parser):
        parser.add_argument('--file')  

    def handle(self, *args, **options):

        email = Email.objects.get(code='UA_WEEKLY')

        if options['file']:
            filename = options['file']
            with open(f'/Users/djamison/Downloads/{filename}', encoding='mac_roman') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                for row in csv_reader:
                    user = row[0]

                    send_mail(
                        email.subject,
                        'See attachment.',
                        email.sender,
                        [user],    # user
                        fail_silently=False,
                        html_message=email.body
                    )

                    print('sent to', user)


