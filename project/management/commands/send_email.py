from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail

from pages.models import Page

from project.models import Email

class Command(BaseCommand):
    help = 'Send Email'
    bcc = 'itscomm.information.systems.shared.account@umich.edu'

    def add_arguments(self, parser):
        parser.add_argument('--email')  

    def handle(self, *args, **options):
        email = Email.objects.get(code=options['email'])
        email.send()